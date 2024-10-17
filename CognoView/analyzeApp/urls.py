from django.urls import path
from . import views


urlpatterns = [
   
    path('',views.home,name='home'),
    path('analyzer/',views.analyze,name='analyze'),
    path('abt/',views.abt,name='abt'),
    path('abf/',views.abf,name='abf'),
    path('questions/', views.get_added_questions, name='questions'),
    path('fetch-questions/<str:batch_identifier>/', views.fetch_questions, name='fetch_questions'),
    path('generate-report/<str:batch_id>/', views.generate_report, name='generate_report'),
    path('report-detail/<str:batch_id>/', views.report_detail, name='report_detail'),
]