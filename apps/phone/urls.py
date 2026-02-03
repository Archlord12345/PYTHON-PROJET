from django.urls import path
from . import views

app_name = 'phone'

urlpatterns = [
    path('', views.index, name='index'),
]
