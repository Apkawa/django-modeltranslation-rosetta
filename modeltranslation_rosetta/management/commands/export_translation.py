# coding: utf-8
from __future__ import unicode_literals

import tablib
from django.core.management.base import BaseCommand
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from applications.core.uds_service.models import ServiceCategory

CATEGORIES_PATH = '%s::' % ServiceCategory.ACTIVE_ROOT_ID


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps, or all apps if no args are specified'

    def export_translation(self, filename):
        models = translator.get_registered_models(abstract=False)
        dataset = tablib.Dataset(headers=['Model', 'object_id', 'field', 'ru', 'en'])
        for model in models:
            opts = translator.get_options_for_model(model)
            fields = [
                [field_name, (
                    build_localized_fieldname(field_name, 'ru'),
                    build_localized_fieldname(field_name, 'en')
                )]
                for field_name in opts.fields.keys()
                ]

            model_name = "%s.%s" % (model._meta.app_label, model._meta.model_name)

            query = model.objects

            if model_name in [
                'uds_service.service',
                'uds_service.servicecategory'
            ]:
                query = query.active()
            elif model_name == 'uds_service.servicevariant':
                query = query.filter(
                    service__is_active=True,
                    service__categories__isnull=False,
                    service__categories__path__startswith=CATEGORIES_PATH
                )

            elif model_name == 'uds_service.serviceoption':
                query = query.filter(
                    variant__service__is_active=True,
                    variant__service__categories__isnull=False,
                    variant__service__categories__path__startswith=CATEGORIES_PATH,
                )

            for o in query.filter().distinct():
                for f, trans_f in fields:
                    translated_data = [getattr(o, tf) or '' for tf in trans_f]

                    if translated_data[0]:
                        dataset.append([model_name, str(o.pk), f] + translated_data)

        with open(filename, 'wb') as f:
            f.write(dataset.xlsx)

    def handle(self, *args, **options):
        self.export_translation("../model_translations.xlsx")
