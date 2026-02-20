from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', include('accounts.urls')),
    path("", include("places.urls")),

]
