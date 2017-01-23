# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict

import six
import tablib
from django.conf import settings
from django.core.management.base import BaseCommand
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po

from ._utils import has_exclude, has_include, parse_model

EXPORT_FILTERS = getattr(settings, 'MODELTRANSLATION_ROSETTA_EXPORT_FILTERS', {})


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'export translations'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=six.text_type)
        # Named (optional) arguments
        parser.add_argument(
            '--from_lang',
            '-fl',
            action='store',
            dest='from_lang',
            default=settings.LANGUAGES[0][0],
            help='from lang',
        )

        parser.add_argument(
            '--to_lang',
            '-tl',
            action='store',
            dest='to_lang',
            default=settings.LANGUAGES[1][0],
            help='to lang',
        )

        parser.add_argument(
            '--format',
            '-f',
            action='store',
            dest='format',
            default='xlsx',
            help='Format. xlsx or po',
        )
        parser.add_argument(
            '--skip-translated',
            action='store_true',
            dest='skip_translated',
            default=False,
            help='skip translated',
        )

    def filter_queryset(self, queryset, model_opts):
        if not EXPORT_FILTERS:
            return queryset
        model_name = '.'.join([model_opts['app_label'], model_opts['model_name']])
        for k in [model_name, None]:
            filter_cb = EXPORT_FILTERS.get(k)
            if filter_cb and callable(filter_cb):
                return filter_cb(queryset, model_opts)

        return queryset

    def collect_translation(self, includes=None, excludes=None):
        """
        :param models: app_label | app_label.Model | app_label.Model.field
        :param excludes: app_label | app_label.Model | app_label.Model.field
        :return:
        """
        models = translator.get_registered_models(abstract=False)
        excludes = excludes and map(parse_model, excludes)
        includes = includes and map(parse_model, includes)

        for model in models:
            opts = translator.get_options_for_model(model)
            meta = model._meta

            fields = {
                field_name: {
                    lang: build_localized_fieldname(field_name, lang)
                    for lang, _ in settings.LANGUAGES
                    }
                for field_name in opts.fields.keys()
                }

            model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)
            model_opts = dict(
                fields=fields,
                app_label=meta.app_label,
                model_name=meta.model_name,
            )

            if has_exclude(model_opts, excludes):
                continue

            if not has_include(model_opts, includes):
                continue

            query = self.filter_queryset(model.objects, model_opts)

            for o in query.distinct():
                for f, trans_f in fields.items():
                    translated_data = {lang: getattr(o, tf) or '' for lang, tf in trans_f.items()}

                    yield dict(
                        model_name=model_name,
                        object_id=str(o.pk),
                        field=f,
                        model=model,
                        obj=o,
                        translated_data=translated_data
                    )

    def export_translation(self, filename, format='xlsx', **options):
        from_lang = options['from_lang']
        to_lang = options['to_lang']
        skip_translated = options['skip_translated']

        translations = self.collect_translation(includes=options.get('includes'), excludes=options.get('excludes'))
        if format == 'xlsx':
            dataset = tablib.Dataset(headers=['Model', 'object_id', 'field', from_lang, to_lang])
            for tr in translations:
                dataset.append([tr['model_name'], tr['object_id'], tr['field'],
                                tr['translated_data'][from_lang],
                                tr['translated_data'][to_lang]
                                ])
            with open(filename, 'wb') as f:
                f.write(dataset.xlsx)

        elif format == 'po':
            catalog = Catalog(locale=to_lang)
            for tr in translations:
                msg_location = ('{model_name}.{field}.{object_id}'.format(**tr), 0)
                msg_id = tr['translated_data'][from_lang].strip().strip('\n')
                msg_str = tr['translated_data'][to_lang].strip().strip('\n')
                if skip_translated and msg_str:
                    continue

                model = tr['model']
                obj = tr['obj']
                comments = ('{app_title}->{model_title}:{obj} [{obj.id}]'.format(
                    app_title=model._meta.app_config.verbose_name,
                    model_title=model._meta.verbose_name,
                    obj=obj
                ),)
                catalog.add(msg_id, msg_str, locations=(msg_location,),
                    auto_comments=comments)

            with open(filename, 'wb') as f:
                write_po(f, catalog)

    def handle(self, **options):
        fmt = options.pop('format', None) or 'xlsx'
        filename = (options.pop('filename', None) or ['../model_translations.%s' % fmt])[0]

        self.export_translation(filename=filename, format=fmt, **options)
