from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
    path('complaint/', views.submit_complaint_ajax, name='submit_complaint'),
    path('submit-complaint-ajax/', views.submit_complaint_ajax, name='submit_complaint_ajax'),

    # ✅ User Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ✅ Success Page
    path('success/', views.success_view, name='success'),
    path('success/<str:complaint_id>/', views.success_view, name='success_with_id'),

    # ✅ Admin Authentication
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ✅ Admin Complaint Management
    path('update-complaint-status/', views.update_complaint_status, name='update_complaint_status'),
    path('add-complaint-feedback/', views.add_complaint_feedback, name='add_complaint_feedback'),

    # ✅ Staff Management
    path('staff-management/', views.staff_management, name='staff_management'),

    # ✅ Complaint Details
    path('complaint/<str:complaint_id>/', views.complaint_details, name='complaint_details'),
]

# ✅ Media files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)