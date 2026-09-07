from activities.views import api
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls), 
    path("", include("activities.urls")),
]

