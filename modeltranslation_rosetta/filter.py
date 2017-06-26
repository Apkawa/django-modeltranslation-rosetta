# coding: utf-8
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.db.models import Q

from .utils import get_model, build_model_name
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname
from .export_translation import TRANSLATED, UNTRANSLATED


class FilterForm(forms.Form):
    TRANSLATE_STATUS = (
        ('', 'All'),
        (UNTRANSLATED, 'Untranslated'),
        (TRANSLATED, 'Translated'),
    )

    translate_status = forms.ChoiceField(label='Translate status',
        choices=TRANSLATE_STATUS,
        required=False,
    )

    fields = forms.MultipleChoiceField(label='Fields',
        choices=(),
        required=False)

    def __init__(self, queryset, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.queryset = queryset
        model = queryset.model
        self.model_info = get_model(build_model_name(model))
        self['fields'].field.choices = [
            (name, model._meta.get_field(name).verbose_name)
            for name in self.model_info['opts'].fields
        ]

    @property
    def qs(self):
        if self.is_valid():
            data = self.cleaned_data
            if not data.get('translate_status'):
                return self.queryset

            translate_status = data['translate_status']

            base_fields = data.get('fields') or self.model_info['opts'].fields.keys()

            fields = [build_localized_fieldname(f, lang)
                      for f in base_fields for lang, desc in
                      settings.LANGUAGES]

            q_filter = Q()
            for f in fields:
                if translate_status == UNTRANSLATED:
                    q_filter |= (Q(**{f + '__isnull': True}) | Q(**{f: ''}))
                else:
                    q_filter &= (Q(**{f + '__isnull': False}) & ~Q(**{f: ''}))
            return self.queryset.filter(q_filter)
        return self.queryset
