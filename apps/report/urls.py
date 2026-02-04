from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('', views.report_view, name='report'),
    path('export/csv/', views.export_report_csv, name='export_csv'),
    path('export/pdf/', views.export_report_pdf, name='export_pdf'),
]
