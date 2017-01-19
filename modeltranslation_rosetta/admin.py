# coding: utf-8
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.contrib import admin

from .custom_admin import CustomAdmin
from .views import ListModelView, EditTranslationView


class TranslationAdmin(CustomAdmin):
    app_label = 'modeltranslation_rosetta'
    module_name = 'trans'
    verbose_name = _('Modeltranslate')
    verbose_name_plural = _('Modeltranslates')

    changelist_view = ListModelView
    change_view = EditTranslationView

    def has_add_permission(self, request):
        return False


TranslationAdmin.register_at(admin.site)
