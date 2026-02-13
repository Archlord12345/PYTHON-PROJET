from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.clients_view, name="index"),
    path("create/", views.create_client, name="create"),
    path("<int:client_id>/update/", views.update_client, name="update"),
    path("<int:client_id>/delete/", views.delete_client, name="delete"),
    path("<int:client_id>/details/", views.client_details, name="details"),
]
