# coding: utf-8
from __future__ import print_function
from __future__ import print_function
from __future__ import unicode_literals

import tablib
from babel.messages.pofile import read_po
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from .settings import (
    DEFAULT_TO_LANG,
    DEFAULT_FROM_LANG
)


def normalize_text(text):
    text = text or ''
    return text.strip()


def build_model_map():
    models_map = {}
    models = translator.get_registered_models(abstract=False)
    for model in models:
        model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)

        models_map[model_name] = model
    return models_map


def group_dataset(dataset):
    group = {}
    key = None
    for row in sorted(dataset, key=lambda r: (r['model_key'], r['object_id'])):
        cur_key = (row['model_key'], row['object_id'])
        if key != cur_key:
            if group:
                yield group
            key = cur_key
            group = row
            group['fields'] = []
        field = {k: row[k]
                 for k in ['field', 'from_lang', 'to_lang']
                 }
        group['fields'].append(field)
    # return last group
    yield group


def calalog_to_dataset(catalog):
    model_map = build_model_map()
    for m in catalog:
        if not m.id:
            pass
        for path, _ in m.locations:
            app_name, model_name, field, object_id = path.split('.')
            model_key = '.'.join([app_name, model_name])
            row = dict(zip(
                ['model_key', 'field', 'object_id', 'app_name', 'model_name'],
                [model_key, field, object_id, app_name, model_name]))
            row['from_lang'] = m.id
            row['to_lang'] = normalize_text(m.string)
            row['model'] = model_map[model_key]
            yield row


def load_translation(grouped_dataset, to_lang=DEFAULT_TO_LANG):
    stat = dict.fromkeys(['update', 'skip', 'fail', 'total'], 0)
    fail_rows = []
    for row in grouped_dataset:
        stat['total'] += 1
        try:
            if import_row(row, to_lang):
                stat['update'] += 1
            else:
                stat['skip'] += 1
        except Exception as e:
            print(e)
            fail_rows.append(row)
            stat['fail'] += 1
    return {'stat': stat, 'fail_rows': fail_rows}


def load_same_rows(rows, to_lang=DEFAULT_TO_LANG, from_lang=DEFAULT_FROM_LANG):
    """

    :param rows:
    :param to_lang:
    :param from_lang:
    :return:
    """
    for r in rows:

        from_name = build_localized_fieldname(r['field'], from_lang)
        to_name = build_localized_fieldname(r['field'], to_lang)

        model = r['model']

        msg_id = r['from_lang'].strip()
        msg_str = normalize_text(r['to_lang']).strip()

        objects = model.objects.filter(**{from_name: msg_id})

        for obj in objects:
            update_fields = []
            if (msg_str
                and normalize_text(getattr(obj, from_name)) == msg_id
                and normalize_text(getattr(obj, to_name)) != msg_str
                ):
                update_fields.append(to_name)
                setattr(obj, to_name, msg_str)
            if not update_fields:
                continue
            print("SAVE", obj, from_name, msg_id)
            try:
                obj.save(update_fields=update_fields)
            except Exception as e:
                print(r['Model'], r['object_id'])
                print(e)


def import_row(row, to_lang):
    model = row['model']
    obj = model.objects.get(id=row['object_id'])

    update_fields = []
    for field in row['fields']:
        to_field_name = build_localized_fieldname(field['field'], to_lang)
        msg_str = normalize_text(field['to_lang']).strip()
        if msg_str and normalize_text(getattr(obj, to_field_name)) != msg_str:
            update_fields.append(to_field_name)
            setattr(obj, to_field_name, msg_str)

    if update_fields:
        obj.save(update_fields=update_fields)
        return True
    return False


def parse_po(stream):
    catalog = read_po(stream)
    return calalog_to_dataset(catalog)


def parse_xlsx(stream):
    return tablib.import_set(stream.read(), format='xlsx').dict
