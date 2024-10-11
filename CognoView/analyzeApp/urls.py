from django.contrib import admin
from django.urls import path
from analyzeApp import views


urlpatterns = [
   
    path('',views.home,name='home'),
    path('analyzer/',views.analyze,name='analyze'),
    path('abt/',views.abt,name='abt'),
    path('abf/',views.abf,name='abf'),
]