from django.urls import path
from . import views

urlpatterns = [
    # ✅ Static Pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('report/', views.report_view, name='report'),
    path('trackcomplaint/', views.track_complaint_view, name='track_complaint'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('offlinehelp/', views.offline_help_view, name='offline_help'),

    # ✅ Complaint Form
    path('complaint/', views.submit_complaint, name='submit_complaint'),

    # ✅ User Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register_view, name='register'),

    # ✅ Success Page (optional direct access)
    path('success/', views.success_view, name='success'),

    # ✅ Admin Authentication (प्रधान के लिए)
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
]