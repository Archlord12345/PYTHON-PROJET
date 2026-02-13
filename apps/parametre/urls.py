from django.urls import path
from . import views

app_name = 'parametre'

urlpatterns = [
    path('', views.index, name='index'),
]
