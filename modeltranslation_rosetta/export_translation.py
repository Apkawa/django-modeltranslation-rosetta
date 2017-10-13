# coding: utf-8
from __future__ import unicode_literals

import tablib
from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po
from io import BytesIO
from modeltranslation.translator import translator
from .import_translation import normalize_text
from .utils import get_cleaned_fields, parse_model, get_opts_from_model
from .settings import (EXPORT_FILTERS, DEFAULT_TO_LANG, DEFAULT_FROM_LANG)

UNTRANSLATED = 'U'
TRANSLATED = 'T'


def allow_export(msg_str, msg_id, translate_status=None):
    if not msg_id:
        return False
    if not translate_status:
        return True
    if translate_status == UNTRANSLATED and not msg_str:
        return True
    if translate_status == TRANSLATED and msg_str:
        return True

    return False


def filter_queryset(queryset, model_opts, export_filters=EXPORT_FILTERS):
    if not export_filters:
        return queryset
    for k in [model_opts['model_key'], None]:
        filter_cb = export_filters.get(k)
        if filter_cb and callable(filter_cb):
            return filter_cb(queryset, model_opts)
    return queryset


def collect_queryset_translations(qs, fields=None):
    model = qs.model
    model_opts = get_opts_from_model(model)

    fields = set(map(lambda f: f.split('.')[-1], fields or []))

    trans_fields = {
        f_name: v for f_name, v in model_opts['fields'].items()
        if not fields or f_name in fields
    }

    for o in qs.distinct():
        for f, trans_f in trans_fields.items():
            translated_data = {lang: normalize_text(getattr(o, tf)) for lang, tf in trans_f.items()}

            yield dict(
                model_key=model_opts['model_key'],
                model_name=model_opts['model_name'],
                object_id=str(o.pk),
                field=f,
                model=model,
                obj=o,
                translated_data=translated_data
            )


def collect_model_translations(model_opts, fields=None):
    """
    :param model_opts:
    :param fields: list of field_name
    :return: iterator
    """
    model = model_opts['model']
    qs = filter_queryset(model.objects, model_opts)
    return collect_queryset_translations(qs, fields)


def collect_models(includes=None, excludes=None):
    """
    :param models: app_label | app_label.Model | app_label.Model.field
    :param excludes: list of app_label | app_label.Model | app_label.Model.field
    :return: iterator of {model_key, model, fields, app_label, model_name}
    """
    models = translator.get_registered_models(abstract=False)
    excludes = excludes and map(parse_model, excludes)
    includes = includes and map(parse_model, includes)

    for model in models:
        only_fields = get_cleaned_fields(model, includes=includes, excludes=excludes)
        if not only_fields:
            continue
        yield get_opts_from_model(model, only_fields)


def collect_translations(
        from_lang=DEFAULT_FROM_LANG,
        to_lang=DEFAULT_TO_LANG,
        translate_status=None,
        includes=False,
        excludes=False,
        queryset=None,
):
    if queryset:
        translations = collect_queryset_translations(queryset, fields=includes)
    else:
        collected_models = collect_models(includes, excludes)
        translations = (
            t for model_opts in collected_models
            for t in collect_model_translations(model_opts)
        )
    for tr in translations:
        msg_id = tr['translated_data'][from_lang]
        msg_str = tr['translated_data'][to_lang]
        if not allow_export(msg_str, msg_id, translate_status):
            continue
        yield tr


def export_po(translations,
              from_lang=DEFAULT_FROM_LANG,
              to_lang=DEFAULT_TO_LANG,
              queryset=None,
              stream=None,
              ):
    stream = stream or BytesIO()
    assert hasattr(stream, 'write') and hasattr(stream, 'seek'), "stream must be file-like object"
    catalog = Catalog(locale=to_lang)
    for tr in translations:
        msg_location = ('{model_key}.{field}.{object_id}'.format(**tr), 0)

        msg_id = tr['translated_data'][from_lang]
        msg_str = tr['translated_data'][to_lang]

        model = tr['model']
        obj = tr['obj']
        comments = ('{app_title}->{model_title}:{obj} [{obj.id}]'.format(
            app_title=model._meta.app_config.verbose_name,
            model_title=model._meta.verbose_name,
            obj=obj
        ),)
        catalog.add(msg_id, msg_str, locations=(msg_location,),
            auto_comments=comments)

    if queryset:
        """
        Особая уличная магия, 
        для корректной выгрузки переводов одного объекта, 
        но он может быть переведен в других объектах
        """
        opts = get_opts_from_model(queryset.model)
        qs_locations = {"%s.%s" % (opts['model_key'], pk) for pk in queryset.values_list('pk', flat=True)}
        new_catalog = Catalog(locale=to_lang)
        for message in catalog:
            locations = set()

            for (loc, n) in message.locations:
                spl = loc.split('.')
                del spl[2]
                locations.add(".".join(spl))

            if locations & qs_locations:
                kw = {k: getattr(message, k) for k in ['auto_comments', 'locations']}

                new_catalog.add(
                    message.id,
                    message.string,
                    **kw
                )
        catalog = new_catalog

    write_po(stream, catalog)
    stream.seek(0)
    return stream


def export_xlsx(stream,
                to_lang,
                translations,
                ):
    dataset = tablib.Dataset(headers=['Model', 'object_id', 'field', from_lang, to_lang])
    for tr in translations:
        msg_id = tr['translated_data']['from_lang'].strip().strip('\n')
        msg_str = tr['translated_data']['to_lang'].strip().strip('\n')

        dataset.append([tr['model_name'], tr['object_id'], tr['field'],
                        msg_id,
                        msg_str,
                        ])
    stream.write(dataset.xlsx)
