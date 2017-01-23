# coding: utf-8
from __future__ import unicode_literals

import os
import six
import tablib
from django.core.management.base import BaseCommand
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


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

    def group_dataset(self, dataset):
        group = {}
        key = None
        for row in sorted(dataset.dict, key=lambda r: (r['Model'], r['object_id'])):
            cur_key = (row['Model'], row['object_id'])
            if key != cur_key:
                if group:
                    yield group
                key = cur_key
                group = row
                group['rows'] = []
            group['rows'].append(row)

    def import_row(self, row):
        Model = self.model_map[row['Model']]
        obj = Model.objects.get(id=row['object_id'])

        update_fields = []
        for r in row['rows']:
            field_name = build_localized_fieldname(r['field'], 'en')
            update_fields.append(field_name)
            setattr(obj, field_name, r['en'])

        obj.save(update_fields=update_fields)

    def import_translation(self, filename, **options):
        stream = open(filename, 'rb').read()
        fmt = os.path.splitext(filename)[1][1:]
        if fmt == 'xlsx':
            dataset = tablib.import_set(stream, format='xlsx')

            for row in self.group_dataset(dataset):
                try:
                    self.import_row(row)
                except Exception as e:
                    print row['Model'], row['object_id']
                    print e
        elif fmt == 'po':
            raise NotImplementedError("TODO import po file")

    def handle(self, **options):
        print options
        filename = options.pop('filename')[0]
        self.import_translation(
            filename,
            **options)
