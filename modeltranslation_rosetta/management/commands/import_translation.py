# coding: utf-8
from __future__ import unicode_literals

import os
import six
import tablib
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from babel.messages.pofile import read_po


def build_model_map():
    models_map = {}
    models = translator.get_registered_models(abstract=False)
    for model in models:
        model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)

        models_map[model_name] = model
    return models_map


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps, or all apps if no args are specified'

    model_map = build_model_map()

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

    def group_dataset(self, dataset):
        group = {}
        key = None
        for row in sorted(dataset, key=lambda r: (r['Model'], r['object_id'])):
            cur_key = (row['Model'], row['object_id'])
            if key != cur_key:
                if group:
                    yield group
                key = cur_key
                group = row
                group['rows'] = []
            group['rows'].append(row)

    def calalog_to_dataset(self, catalog, from_lang, to_lang):
        for m in catalog:
            if not m.id:
                pass
            for path, _ in m.locations:
                app_name, model_name, field, object_id = path.split('.')
                Model = '.'.join([app_name, model_name])
                row = dict(zip(
                    ['Model', 'field', 'object_id', 'app_name', 'model_name'],
                    [Model, field, object_id, app_name, model_name]))
                row[from_lang] = m.id
                row[to_lang] = m.string
                yield row

    def import_fail_rows(self, rows, to_lang, from_lang):

        for r in rows:
            field_name = build_localized_fieldname(r['field'], to_lang)
            from_name = build_localized_fieldname(r['field'], from_lang)

            Model = self.model_map[r['Model']]
            objects = Model.objects.filter(**{from_name: r[from_lang].strip()})

            for obj in objects:
                update_fields = []
                if (r[to_lang]
                    and getattr(obj, from_name).strip() == r[from_lang].strip()
                    and (getattr(obj, field_name) or '').strip() != (r[to_lang] or '').strip()
                    ):
                    update_fields.append(field_name)
                    setattr(obj, field_name, r[to_lang])
                if not update_fields:
                    continue
                print "SAVE", obj, from_name, r[from_lang]
                try:
                    obj.save(update_fields=update_fields)
                except Exception as e:
                    print r['Model'], r['object_id']
                    print e

    def import_row(self, row, to_lang):
        Model = self.model_map[row['Model']]
        obj = Model.objects.get(id=row['object_id'])

        update_fields = []
        for r in row['rows']:
            field_name = build_localized_fieldname(r['field'], to_lang)

            if r[to_lang] and getattr(obj, field_name) != r[to_lang]:
                update_fields.append(field_name)
                setattr(obj, field_name, r[to_lang])

        if update_fields:
            obj.save(update_fields=update_fields)

    def import_translation(self, filename, **options):
        fmt = os.path.splitext(filename)[1][1:]
        from_lang = options['from_lang']
        to_lang = options['to_lang']

        fail_rows = []
        flatten_dataset = []

        if fmt == 'xlsx':
            with open(filename, 'rb') as stream:
                flatten_dataset = tablib.import_set(stream.read(), format='xlsx').dict

            for row in self.group_dataset(flatten_dataset):
                try:
                    self.import_row(row, to_lang)
                except Exception as e:
                    fail_rows.append(row)
                    print row['Model'], row['object_id']
                    print e

        elif fmt == 'po':
            with open(filename, 'rb') as stream:
                catalog = read_po(stream)

            flatten_dataset = self.calalog_to_dataset(catalog, from_lang=from_lang, to_lang=to_lang)

            for row in self.group_dataset(flatten_dataset):
                try:
                    self.import_row(row, to_lang)
                except Exception as e:
                    fail_rows.append(row)
                    print row['Model'], row['object_id']
                    print e

        self.import_fail_rows(flatten_dataset, from_lang=from_lang, to_lang=to_lang)

    def handle(self, **options):
        print options
        filename = options.pop('filename')[0]
        self.import_translation(
            filename,
            **options)
