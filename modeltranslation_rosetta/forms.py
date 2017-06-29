# coding: utf-8
from __future__ import unicode_literals
from django import forms
from django.forms.formsets import TOTAL_FORM_COUNT

from django.forms.models import modelform_factory, formset_factory, fields_for_model
from django.utils.translation import ungettext

from .utils import build_localized_fieldname
from .import_translation import parse_po
from .utils import get_model, build_model_name


class ImportForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        f = self.cleaned_data['file']
        try:
            return parse_po(f)
        except:
            raise forms.ValidationError("Invalid po file")


class FieldFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self._only_fields = kwargs.pop('fields', None)
        super(FieldFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['fields'] = self._only_fields
        return super(FieldFormSet, self)._construct_form(i, **kwargs)

    def get_changed_forms(self):
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if form.has_changed():
                yield form

    def clean(self):
        pass

    def is_valid(self):
        """
        Returns True if every form in self.forms is valid.
        """
        if not self.is_bound:
            return False
        # We loop over every form.errors here rather than short circuiting on the
        # first failure to make sure validation gets triggered for every form.
        forms_valid = True
        # This triggers a full clean.
        self.errors
        for form in self.get_changed_forms():
            if self.can_delete:
                if self._should_delete_form(form):
                    # This form is going to be deleted so any of its errors
                    # should not cause the entire formset to be invalid.
                    continue
            forms_valid &= form.is_valid()
        return forms_valid and not self.non_form_errors()

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self._non_form_errors.
        """
        self._errors = []
        self._non_form_errors = self.error_class()

        if not self.is_bound:  # Stop further processing.
            return
        for form in self.get_changed_forms():
            self._errors.append(form.errors)
        try:
            if (self.validate_max and
                            self.total_form_count() - len(self.deleted_forms) > self.max_num) or \
                            self.management_form.cleaned_data[TOTAL_FORM_COUNT] > self.absolute_max:
                raise forms.ValidationError(ungettext(
                    "Please submit %d or fewer forms.",
                    "Please submit %d or fewer forms.", self.max_num) % self.max_num,
                    code='too_many_forms',
                                            )
            if (self.validate_min and
                            self.total_form_count() - len(self.deleted_forms) < self.min_num):
                raise forms.ValidationError(ungettext(
                    "Please submit %d or more forms.",
                    "Please submit %d or more forms.", self.min_num) % self.min_num,
                    code='too_few_forms')
            # Give self.clean() a chance to do cross-form validation.
            self.clean()
        except forms.ValidationError as e:
            self._non_form_errors = self.error_class(e.error_list)


class FieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._only_fields = kwargs.pop('fields', None)
        super(FieldForm, self).__init__(*args, **kwargs)
        self.model_info = get_model(build_model_name(self.instance))
        self.build_fields()

    def get_translated_fields(self):
        opts = self.model_info['opts']
        fields = [
            [field_name, (
                build_localized_fieldname(field_name, 'ru'),
                build_localized_fieldname(field_name, 'en')
            )]
            for field_name in sorted(opts.fields.keys())
            if not self._only_fields or field_name in self._only_fields
        ]
        return fields

    def build_fields(self):
        fields = []

        for b_f, translated_fields in self.get_translated_fields():
            fields.extend(translated_fields)

        self._meta.fields += fields
        self.fields.update(fields_for_model(self.model_info['model'], fields))

    def group_fields(self):
        fields = []
        for b_f, translated_fields in self.get_translated_fields():
            fields.append([self[tf] for tf in translated_fields])
        return fields
