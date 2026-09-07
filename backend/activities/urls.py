from django.urls import path
from . import views
from .views import api

app_name = "activities"

urlpatterns = [
    # vista original
    path("", views.activity_list, name="list"),

    # versiones de endpoints 
    # v1
    path("api/v1/activities/<str:activity_id>", views.activity_detail, name="api-detail"),
    # v2 
    path("api/v2/activities/<str:activity_id>", views.activity_detail_2, name="api-detail-2"),

    # Inscripción v1
    path("api/v1/me/enrollments", views.my_enrollments_list, name="enrollment-list"),
    path("api/v1/me/enrollments/<str:activity_id>", views.activity_enrollment_api_put_delete, name="enrollment-detail"),
    
    # Inscripción v2 (reutiliza vistas de v1)
    path("api/v2/me/enrollments", views.my_enrollments_list, name="enrollment-list-2"),
    path("api/v2/me/enrollments/<str:activity_id>", views.activity_enrollment_api_put_delete, name="enrollment-detail-2"),

]