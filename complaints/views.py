from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint, AdminProfile, ComplaintTracking, StaffMember
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import qrcode
import io
import base64

# ✅ Home Page View
def home(request):
    return render(request, 'complaints/home.html')

# ✅ About Page View
def about_view(request):
    return render(request, 'complaints/about.html')

# ✅ Report Complaint View (Updated for new model)
def report_view(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            location = request.POST.get('location', '').strip()
            issue = request.POST.get('issue', '').strip()
            description = request.POST.get('description', '').strip()
            photo = request.FILES.get('photo')
            
            # Validate required fields
            if not all([name, location, issue]):
                messages.error(request, 'Name, location and issue description are required.')
                return render(request, 'complaints/report.html')
            
            # Use issue as description if description is empty
            if not description:
                description = issue
            
            # Create complaint (QR code will be auto-generated in save method)
            complaint = Complaint.objects.create(
                name=name,
                location=location,
                issue=issue,
                description=description,
                photo=photo,
                status='submitted'
            )
            
            # Create initial tracking record
            ComplaintTracking.objects.create(
                complaint=complaint,
                status='submitted',
                notes='Complaint registered'
            )
            
            messages.success(request, f'Complaint successfully registered! Your complaint ID is: {complaint.complaint_id}')
            return redirect('success_view', complaint_id=complaint.complaint_id)
            
        except Exception as e:
            messages.error(request, f'Error registering complaint: {str(e)}')
            return render(request, 'complaints/report.html')
    
    return render(request, 'complaints/report.html')

# ✅ Original submit_complaint function (for backward compatibility)
def submit_complaint(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        issue = request.POST.get('issue', '').strip()
        photo = request.FILES.get('photo')

        if not all([name, location, issue, photo]):
            return render(request, 'complaints/form.html', {
                'error': 'All fields are mandatory. Please try again.'
            })

        # Create complaint with new model
        complaint = Complaint.objects.create(
            name=name,
            location=location,
            issue=issue,
            description=issue,  # Using issue as description
            photo=photo,
            status='submitted'
        )

        # Create tracking record
        ComplaintTracking.objects.create(
            complaint=complaint,
            status='submitted',
            notes='Complaint registered'
        )

        return render(request, 'complaints/success.html', {'complaint': complaint})

    return render(request, 'complaints/form.html')

# ✅ AJAX Complaint Submission (for your JavaScript form)
@csrf_exempt
def submit_complaint_ajax(request):
    if request.method == 'POST':
        try:
            # Check if it's JSON data or form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                location = data.get('location', '').strip()
                description = data.get('description', '').strip()
                photo_data = data.get('photo')  # Base64 image data
            else:
                # Handle form data
                name = request.POST.get('name', '').strip()
                location = request.POST.get('location', '').strip()
                description = request.POST.get('description', '').strip()
                photo = request.FILES.get('photo')
                photo_data = None
            
            if not all([name, location, description]):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are mandatory.'
                })
            
            # Create complaint
            complaint = Complaint.objects.create(
                name=name,
                location=location,
                issue=description,
                description=description,
                status='submitted'
            )
            
            # Handle photo if provided
            if photo_data:
                # Base64 image
                try:
                    format, imgstr = photo_data.split(';base64,')
                    ext = format.split('/')[-1]
                    photo_file = ContentFile(
                        base64.b64decode(imgstr), 
                        name=f"complaint_{complaint.complaint_id}.{ext}"
                    )
                    complaint.photo = photo_file
                    complaint.save()
                except Exception as e:
                    print(f"Photo processing error: {e}")
            elif photo:
                # Regular file upload
                complaint.photo = photo
                complaint.save()
            
            # Create tracking record
            ComplaintTracking.objects.create(
                complaint=complaint,
                status='submitted',
                notes='Complaint registered'
            )
            
            return JsonResponse({
                'success': True,
                'complaint_id': complaint.complaint_id,
                'message': 'Complaint successfully registered!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# ✅ Track Complaint View (Updated)
def track_complaint_view(request):
    complaint_id = request.GET.get('complaint_id', '')
    complaint = None
    tracking_history = []
    
    if complaint_id:
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            # Get tracking history
            tracking_history = ComplaintTracking.objects.filter(complaint=complaint).order_by('-updated_at')
        except Complaint.DoesNotExist:
            complaint = None
            messages.error(request, f'Complaint ID {complaint_id} not found.')
    
    return render(request, 'complaints/trackcomplaint.html', {
        'complaint': complaint,
        'complaint_id': complaint_id,
        'tracking_history': tracking_history
    })

# ✅ Success View with Complaint ID
def success_view(request, complaint_id=None):
    complaint = None
    if complaint_id:
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
        except Complaint.DoesNotExist:
            messages.error(request, 'Complaint not found.')
    
    return render(request, "complaints/success.html", {'complaint': complaint})

# ✅ Dashboard View (FIXED - Added current_time)
def dashboard_view(request):
    # Public dashboard - show all complaints statistics
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    pending_complaints = Complaint.objects.filter(status__in=['submitted', 'verified']).count()
    
    # Recent complaints
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:10]
    
    # Calculate resolution rate
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = (resolved_complaints / total_complaints) * 100
    
    return render(request, 'complaints/publicDeshBoard.html', {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'recent_complaints': recent_complaints,
        'resolution_rate': resolution_rate,
        'current_time': timezone.now()  # ✅ FIX: Added missing context variable
    })

# ✅ Offline Help View
def offline_help_view(request):
    return render(request, 'complaints/offlinehelp.html')

# ✅ User Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'complaints/user.html')

# ✅ User Registration View
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')

    return render(request, 'complaints/register.html')

# ✅ Admin Login View (For Chief)
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                admin_profile = AdminProfile.objects.get(user=user)
                login(request, user)
                messages.success(request, f'Welcome! {admin_profile.village_name}')
                return redirect('admin_dashboard')
            except AdminProfile.DoesNotExist:
                messages.error(request, 'You do not have administrative access.')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'complaints/admin_login.html')

# ✅ Admin Dashboard View (Only complaints from their village)
@login_required
def admin_dashboard(request):
    try:
        admin_profile = AdminProfile.objects.get(user=request.user)
        complaints = Complaint.objects.filter(location__iexact=admin_profile.village_name).order_by('-created_at')
        
        # Statistics
        total = complaints.count()
        submitted = complaints.filter(status='submitted').count()
        verified = complaints.filter(status='verified').count()
        resolved = complaints.filter(status='resolved').count()
        
        # Calculate resolution rate
        resolution_rate = 0
        if total > 0:
            resolution_rate = (resolved / total) * 100
        
        return render(request, 'complaints/admin_dashboard.html', {
            'complaints': complaints,
            'village': admin_profile.village_name,
            'total_complaints': total,
            'submitted_complaints': submitted,
            'verified_complaints': verified,
            'resolved_complaints': resolved,
            'resolution_rate': resolution_rate,
            'current_time': timezone.now()
        })
    except AdminProfile.DoesNotExist:
        messages.error(request, 'You do not have administrative access.')
        return redirect('admin_login')

# ✅ Update Complaint Status (Admin)
@login_required
@csrf_exempt
def update_complaint_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            status = data.get('status')
            notes = data.get('notes', '')
            
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            
            # Verify admin has access to this village's complaints
            admin_profile = AdminProfile.objects.get(user=request.user)
            if complaint.location.lower() != admin_profile.village_name.lower():
                return JsonResponse({
                    'success': False,
                    'message': 'You are not authorized to access this complaint.'
                })
            
            # Update complaint status
            old_status = complaint.status
            complaint.status = status
            
            # Update timestamps
            if status == 'verified' and not complaint.verified_at:
                complaint.verified_at = timezone.now()
            elif status == 'resolved' and not complaint.resolved_at:
                complaint.resolved_at = timezone.now()
            
            complaint.save()
            
            # Create tracking record
            ComplaintTracking.objects.create(
                complaint=complaint,
                status=status,
                notes=notes or f'Status changed: {old_status} → {status}',
                updated_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Status successfully updated!'
            })
            
        except Complaint.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Complaint not found.'
            })
        except AdminProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No administrative access.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# ✅ Add Feedback to Complaint
@login_required
@csrf_exempt
def add_complaint_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            feedback = data.get('feedback')
            
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            complaint.feedback = feedback
            complaint.status = 'feedback'
            complaint.save()
            
            # Create tracking record
            ComplaintTracking.objects.create(
                complaint=complaint,
                status='feedback',
                notes=f'Feedback given: {dict(Complaint.FEEDBACK_CHOICES).get(feedback)}',
                updated_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Feedback successfully recorded!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# ✅ Logout View
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home')

# ✅ Complaint Details View
def complaint_details(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    tracking_history = ComplaintTracking.objects.filter(complaint=complaint).order_by('-updated_at')
    
    return render(request, 'complaints/complaint_details.html', {
        'complaint': complaint,
        'tracking_history': tracking_history
    })

# ✅ Staff Management View (for admin)
@login_required
def staff_management(request):
    try:
        admin_profile = AdminProfile.objects.get(user=request.user)
        staff_members = StaffMember.objects.filter(admin_profile=admin_profile, is_active=True)
        
        if request.method == 'POST':
            # Add new staff member
            username = request.POST.get('username')
            designation = request.POST.get('designation')
            phone_number = request.POST.get('phone_number')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password='default123'  # Default password
                )
                StaffMember.objects.create(
                    user=user,
                    admin_profile=admin_profile,
                    designation=designation,
                    phone_number=phone_number
                )
                messages.success(request, 'Staff member successfully added!')
                return redirect('staff_management')
        
        return render(request, 'complaints/staff_management.html', {
            'staff_members': staff_members,
            'village': admin_profile.village_name
        })
        
    except AdminProfile.DoesNotExist:
        messages.error(request, 'You do not have administrative access.')
        return redirect('admin_login')

# ✅ Get Complaint Statistics (API)
@csrf_exempt
def get_complaint_stats(request):
    """API for complaint statistics"""
    total = Complaint.objects.count()
    submitted = Complaint.objects.filter(status='submitted').count()
    verified = Complaint.objects.filter(status='verified').count()
    resolved = Complaint.objects.filter(status='resolved').count()
    
    return JsonResponse({
        'total': total,
        'submitted': submitted,
        'verified': verified,
        'resolved': resolved
    })