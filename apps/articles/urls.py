from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.liste_articles, name='liste_articles'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('creer/', views.creer_article, name='creer_article'),
    path('editer/<int:pk>/', views.editer_article, name='editer_article'),
    path('supprimer/<int:pk>/', views.supprimer_article, name='supprimer_article'),
    path('importer/', views.importer_articles, name='importer_articles'),
    path('exporter/', views.export_articles, name='export_articles'),
]
