from django.urls import path
from . import views

urlpatterns = [
    # Static Pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('report/', views.report_view, name='report'),
    path('trackcomplaint/', views.track_complaint_view, name='track_complaint'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('offlinehelp/', views.offline_help_view, name='offline_help'),

    # Complaint Form
    path('complaint/', views.submit_complaint, name='submit_complaint'),

    # User Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register_view, name='register'),  # ✅ Added to fix NoReverseMatch

    # Optional: Direct success page (if needed separately)
    path('success/', views.success_view, name='success'),  # ✅ Optional view if you want direct access
]