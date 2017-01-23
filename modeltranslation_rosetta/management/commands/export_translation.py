# coding: utf-8
from __future__ import unicode_literals

import tablib
from django.conf import settings
from django.core.management.base import BaseCommand
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps, or all apps if no args are specified'

    def add_arguments(self, parser):
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

    def parse_model(self, model):
        return dict(zip(['app_label', 'model', 'field'], model.split('.') + [None] * 2))

    def collect_translation(self, includes=None, excludes=None):
        """
        :param models: app_label | app_label.Model | app_label.Model.field
        :param excludes: app_label | app_label.Model | app_label.Model.field
        :return:
        """
        models = translator.get_registered_models(abstract=False)
        excludes = excludes and map(self.parse_model, excludes)
        includes = includes and map(self.parse_model, includes)

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

            if excludes:
                _exclude = False
                for i in excludes:
                    _exclude |= i['app_label'] == meta.app_label and i['model'] is None
                    _exclude |= (i['app_label'] == meta.app_label
                                 and i['model'] == meta.model_name
                                 and i['field'] is None
                                 )

                    for f, tr_f in fields:
                        if i['app_label'] == meta.app_label and i['model'] == meta.model_name and i['field'] == f:
                            del fields[f]

                if _exclude or not fields:
                    break

            if includes:
                _include = False
                for i in includes:
                    _include |= i['app_label'] == meta.app_label and i['model'] is None
                    _include |= (
                        i['app_label'] == meta.app_label
                        and i['model'] == meta.model_name
                        and i['field'] is None
                    )
                    for f, tr_f in fields:
                        if (i['app_label'] == meta.app_label
                            and i['model'] == meta.model_name
                            and i['field']
                            and i['field'] != f):
                            del fields[f]
                if not _include or not fields:
                    break

            model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)

            query = model.objects

            for o in query.filter().distinct():
                for f, trans_f in fields.items():
                    translated_data = {lang: getattr(o, tf) or '' for lang, tf in trans_f.items()}

                    yield dict(
                        model_name=model_name,
                        object_id=str(o.pk),
                        field=f,
                        translated_data=translated_data
                    )

    def export_translation(self, filename, format='xlsx', **options):
        from_lang = options['from_lang']
        to_lang = options['to_lang']
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
                msg_id = tr['translated_data'][from_lang]
                msg_str = tr['translated_data'][to_lang]
                catalog.add(msg_id, msg_str, locations=(msg_location,))
            with open(filename, 'wb') as f:
                write_po(f, catalog)

    def handle(self, filename=None, **options):
        fmt = options.pop('format', None) or 'xlsx'

        self.export_translation(filename=filename or '../model_translations.%s' % fmt, format=fmt, **options)
