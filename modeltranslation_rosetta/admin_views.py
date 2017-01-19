# coding: utf-8
from __future__ import unicode_literals

from functools import wraps

from django.contrib.admin.options import get_content_type_for_model, IS_POPUP_VAR
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, FormView


class AdminViewMixin(object):
    admin = None
    view_type = None
    object = None
    form_url = None
    pk_url_kwarg = 'pk'

    add_perm = None
    change_perm = None
    delete_perm = None
    readonly_perm = None

    show_delete = show_save = show_save_and_continue = True
    show_only_save = False

    def _get_admin_attr(self, name):
        app_label = getattr(self.admin, name, None)
        if not app_label:
            app_label = getattr(self.admin.model._meta, name)
        return app_label

    def is_add(self):
        return not self.kwargs.get(self.pk_url_kwarg)

    def has_add_permission(self, request):
        perm = self.add_perm
        if perm is None:
            perm = self.admin.has_add_permission(request)
        return perm

    def has_change_permission(self, request, obj):
        perm = self.change_perm
        if perm is None:
            perm = self.admin.has_change_permission(request, obj)
        return perm

    def has_readonly_permission(self, request, obj=None):
        perm = self.readonly_perm
        if perm is None and hasattr(self.admin, 'has_readonly_permission'):
            perm = self.admin.has_readonly_permission(request, obj)
        return perm

    def has_delete_permission(self, request, obj):
        perm = self.delete_perm
        if perm is None:
            perm = self.admin.has_delete_permission(request, obj),
        return perm

    def get_admin_context(self, **extra_context):
        admin = self.admin
        obj = self.object

        self.request.current_app = admin.admin_site.name

        view_on_site_url = admin.get_view_on_site_url(obj)
        context = dict(
            admin.admin_site.each_context(self.request),
            change=not self.is_add(),
            add=self.is_add(),
            object=obj,
            object_id=obj and obj.id,
            opts=admin.model._meta,
            app_label=self._get_admin_attr('app_label'),
            verbose_name=self._get_admin_attr('verbose_name'),
            save_as=False,
            save_on_top=False,
            is_popup=(IS_POPUP_VAR in self.request.POST or
                      IS_POPUP_VAR in self.request.GET),
            is_popup_var=IS_POPUP_VAR,

            content_type_id=get_content_type_for_model(admin.model).pk,
            has_absolute_url=view_on_site_url is not None,
            absolute_url=view_on_site_url,
            form_url=self.kwargs.get('form_url') or '',

            has_add_permission=self.has_add_permission(self.request),
            has_change_permission=self.has_change_permission(self.request, self.object),
            has_delete_permission=self.has_delete_permission(self.request, self.object),
            has_readonly_permission=self.has_readonly_permission(self.request, self.object),

            has_file_field=True,
            show_delete=self.show_delete,
            show_save=self.show_save,
            show_save_and_continue=self.show_save_and_continue,
            show_only_save=self.show_save,
        )
        return context

    def get_context_data(self, **kwargs):
        context = super(AdminViewMixin, self).get_context_data(**kwargs)
        context.update(self.get_admin_context())
        if hasattr(self.admin, 'get_extra_context'):
            context.update(self.admin.get_extra_context(self.request, object_id=context.get('object_id')))
        return context


class AdminObjectView(AdminViewMixin):
    def get_queryset(self):
        return self.admin.get_queryset(self.request)

    def get_object(self, queryset=None):
        obj = self.admin.get_object(self.request, self.kwargs[self.pk_url_kwarg])
        if obj is None:
            raise ObjectDoesNotExist("Not found")
        return obj


class AdminTemplateView(AdminViewMixin, TemplateView):
    template_name = None


class AdminFormView(AdminViewMixin, FormView):
    pass


class AdminDetailView(AdminObjectView, DetailView):
    def get_context_data(self, **kwargs):
        context = AdminObjectView.get_context_data(self, **kwargs)
        context.update(DetailView.get_context_data(self, **kwargs))
        return context

    def dispatch(self, request, object_id=None, form_url='', extra_context=None, **kwargs):
        self.kwargs = {
            'pk': object_id,
            'form_url': form_url,
            'extra_context': extra_context
        }
        self.kwargs.update(kwargs)
        return super(AdminDetailView, self).dispatch(request, **self.kwargs)


class AdminUpdateView(AdminObjectView, UpdateView):
    success_url = ''

    def get_admin_context(self, **extra_context):
        context = super(AdminUpdateView, self).get_admin_context(**extra_context)
        context.update(self.admin.get_extra_context(self.request, object_id=None))
        return context

    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        context.update(self.get_admin_context())
        return context

    def form_invalid(self, form):
        return super(AdminUpdateView, self).form_invalid(form)

    def form_valid_response(self, form):
        if self.is_add():
            return self.admin.response_add(self.request, self.object)
        return self.admin.response_change(self.request, self.object)

    def form_valid(self, form):
        self.object = form.save()
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
        return self.form_valid_response(form)

    def dispatch(self, request, object_id=None, form_url='', extra_context=None, **kwargs):
        self.kwargs = {
            'pk': object_id,
            'form_url': form_url,
            'extra_context': extra_context,

        }
        self.kwargs.update(**kwargs)
        return super(AdminUpdateView, self).dispatch(request, **self.kwargs)


class AdminAddFormView(AdminUpdateView):
    def get_object(self, queryset=None):
        return None


class AdminChangeFormView(AdminUpdateView):
    is_allow_add = True

    def get_admin_context(self, **extra_context):
        context = AdminObjectView.get_admin_context(self, **extra_context)
        context.update(self.admin.get_extra_context(self.request, object_id=self.object and self.object.id))
        return context

    def get_object(self, queryset=None):
        try:
            return super(AdminChangeFormView, self).get_object(queryset)
        except ObjectDoesNotExist as e:
            if not self.is_allow_add:
                raise Http404("Not found")


def admin_view_class(view_class, view_type='change', template_name=None):
    def decorator(func):
        @wraps(func)
        def wrap(self, request, *args, **kwargs):
            view = getattr(func, '_view', None)
            if not view:
                view_kw = {}
                if template_name:
                    view_kw['template_name'] = template_name
                view = view_class.as_view(admin=self, view_type=view_type, **view_kw)
                setattr(func, '_view', None)
            return view(request, *args, **kwargs)

        return wrap

    return decorator
