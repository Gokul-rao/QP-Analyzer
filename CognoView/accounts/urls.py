from django.contrib import admin
from django.urls import path
from accounts import views


urlpatterns = [
   
    path('accounts/signup/',views.SignupPage,name='signup'),
    path('accounts/login/',views.LoginPage,name='login'),
    path('',views.HomePage,name='home'),
    path('accounts/logout/',views.LogoutPage,name='logout'),
]