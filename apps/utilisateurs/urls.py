from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
