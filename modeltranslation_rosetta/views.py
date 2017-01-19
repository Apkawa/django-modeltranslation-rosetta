# coding: utf-8
from __future__ import unicode_literals
from django.forms.models import modelform_factory, modelformset_factory
from functools import partial, wraps

from django.views.generic.list import ListView, MultipleObjectMixin

from .admin_views import AdminTemplateView, AdminFormView

from .utils import get_models, get_model
from .templates import get_template

from .forms import FieldForm, FieldFormSet

from .filter import FilterForm


class ListModelView(AdminTemplateView):
    template_name = get_template('list_models.html')

    def get_context_data(self, **kwargs):
        context = super(ListModelView, self).get_context_data(**kwargs)
        context['translated_models'] = get_models()
        return context


class EditTranslationView(AdminFormView, MultipleObjectMixin):
    template_name = get_template('edit_translation.html')
    form_class = FieldForm
    paginate_by = 10

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def form_valid(self, form):
        form.save()
        return super(EditTranslationView, self).form_valid(form)

    def get_model_info(self):
        return get_model(*self.args)

    def get_model(self):
        return self.get_model_info()['model']

    def filter_queryset(self, queryset):
        self.filter_form = FilterForm(queryset, data=self.request.GET)
        return self.filter_form.qs

    def get_queryset(self):
        return self.get_model().objects.filter()

    def get_form_class(self):
        return modelform_factory(self.get_model(), form=self.form_class, fields=[])

    def get_form(self, form_class=None):
        self.object_list = queryset = self.filter_queryset(self.get_queryset())

        form_kw = self.get_form_kwargs()
        form_class = self.get_form_class()

        ModelFormSet = modelformset_factory(self.get_model(),
            form=form_class,
            formset=FieldFormSet,
            extra=0,
            can_delete=False,
            can_order=False
        )
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset=queryset, page_size=self.paginate_by)
        queryset = self.get_model().objects.filter(id__in=list(queryset.values_list('id', flat=True)))
        return ModelFormSet(
            queryset=queryset,
            fields=self.filter_form.cleaned_data.get('fields'),
            **form_kw)

    def get_context_data(self, **kwargs):
        context = super(EditTranslationView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        return context
