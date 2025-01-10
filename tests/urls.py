# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = []

urlpatterns += [
    url(r"^admin/", admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.views.i18n import javascript_catalog

js_info_dict = {
    # 'packages': ('your.app.package',),
}
urlpatterns += [
    url(r"^jsi18n/$", javascript_catalog, js_info_dict, name="javascript-catalog"),
]
