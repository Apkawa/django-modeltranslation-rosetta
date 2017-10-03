# coding: utf-8
from __future__ import unicode_literals
from io import BytesIO

from django.contrib import messages
from django.db.transaction import atomic
from django.forms.models import modelform_factory, modelformset_factory
from functools import partial, wraps

from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic.list import ListView, MultipleObjectMixin

from modeltranslation_rosetta.import_translation import load_translation, group_dataset, load_same_rows
from .admin_views import AdminTemplateView, AdminFormView

from .utils import get_models, get_model
from .utils.response import FileResponse
from .templates import get_template

from .forms import FieldForm, FieldFormSet, ImportForm

from .filter import FilterForm
from .export_translation import export_po, collect_translations, get_opts_from_model


class ListModelView(AdminTemplateView):
    template_name = get_template('list_models.html')

    def get_context_data(self, **kwargs):
        context = super(ListModelView, self).get_context_data(**kwargs)
        context['translated_models'] = get_models()
        context['import_form'] = ImportForm()
        return context

    def get_filename(self, includes=None):
        now = localtime(timezone.now())
        if includes:
            includes = " ".join(includes)
        else:
            includes = 'All models'

        return '{includes}_{now:%Y-%m-%d %H:%M}.po'.format(
            includes=includes,
            now=now)

    def post(self, request, *args, **kwargs):
        if request.GET.get('_export') == 'po':
            from_lang = 'ru'
            to_lang = 'en'
            includes = request.POST.getlist('include') or None
            translations = collect_translations(
                from_lang=from_lang,
                to_lang=to_lang,
                includes=includes,
            )
            stream = BytesIO()
            export_po(stream,
                to_lang=to_lang,
                translations=translations
            )
            stream.seek(0)
            response = FileResponse(stream.read(), self.get_filename(includes))
            return response

        return redirect('.')


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

    def get_filename(self):
        model_key = self.get_model_info()['model_key']
        parts = [
            model_key,
            " ".join(self.filter_form.cleaned_data.get('fields') or []),
            self.filter_form.cleaned_data.get('search')
        ]
        now = localtime(timezone.now())

        return '{name}_{now:%Y-%m-%d %H:%M}.po'.format(
            name="_".join(filter(None, parts)),
            now=now)

    def get(self, request, *args, **kwargs):
        response = super(EditTranslationView, self).get(*args, **kwargs)
        if request.GET.get('_export') == 'po':
            from_lang = 'ru'
            to_lang = 'en'
            includes = None

            fields = self.filter_form.cleaned_data.get('fields')
            if fields:
                opts = get_opts_from_model(self.object_list.model)
                includes = ['.'.join([opts['model_key'], f]) for f in fields]

            translations = collect_translations(
                from_lang=from_lang,
                to_lang=to_lang,
                translate_status=self.filter_form.cleaned_data['translate_status'],
                queryset=self.get_queryset(),
                includes=includes,
            )
            stream = BytesIO()
            export_po(
                stream,
                to_lang=to_lang,
                translations=translations,
                queryset=self.object_list
            )
            stream.seek(0)
            response = FileResponse(stream.read(), self.get_filename())
            return response
        return response


class ImportPOView(AdminFormView):
    form_class = ImportForm
    template_name = 'modeltranslation_rosetta/default/import.html'

    @atomic
    def form_valid(self, form):
        from_lang = 'ru'
        to_lang = 'en'
        flatten_dataset = form.cleaned_data['file']
        result = load_translation(
            group_dataset(flatten_dataset),
            to_lang=to_lang)

        messages.add_message(self.request, messages.SUCCESS, result['stat'])

        load_same_rows(flatten_dataset, from_lang=from_lang, to_lang=to_lang)
        return redirect('.')
