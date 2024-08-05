from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='Login'),
    path('register/', views.RegisterView.as_view(), name='Register'),
    path('profile/', views.UserProfileView.as_view(), name='Profile'),
]
