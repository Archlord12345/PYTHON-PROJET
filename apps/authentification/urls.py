from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.create_view, name='signup'),

    path('client/inscription/', views.client_signup, name='client_signup'),
    path('client/connexion/', views.client_signin, name='client_signin'),

]
