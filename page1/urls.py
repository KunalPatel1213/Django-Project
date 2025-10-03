from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('report/', views.report_view, name='report'),
    path('trackcomplaint/', views.track_complaint_view, name='track_complaint'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('offlinehelp/', views.offline_help_view, name='offline_help'),
]