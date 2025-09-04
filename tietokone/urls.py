from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tietokone, name='tietokone'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),  # Neue Route
]