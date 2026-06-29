from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    
    path("dashboard/", views.dashboard, name="dashboard"),

    path("api/generate-password/", views.generate_password_api, name="generate_password"),

    path('delete/<int:pk>/', views.delete_credential, name='delete_credential'),
]