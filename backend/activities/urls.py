from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    # vista original
    path("", views.activity_list, name="list"),

    # 
    path("api/v1/activities", views.activity_api_list, name="api-list"),
    path("api/v1/activities/<str:activity_id>", views.activity_detail, name="api-detail"),

    # Inscripción
    path("api/v1/me/enrollments", views.my_enrollments_list, name="enrollment-list"),
    path("api/v1/me/enrollments/<str:activity_id>", views.activity_enrollment_api_put_delete, name="enrollment-detail"),
]