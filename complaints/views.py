from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Complaint
from django.core.files.base import ContentFile
import qrcode
import io

# ✅ Complaint Submission View
def submit_complaint(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        issue = request.POST.get('issue', '').strip()
        photo = request.FILES.get('photo')

        if not all([name, location, issue, photo]):
            return render(request, 'complaints/form.html', {
                'error': 'सभी फ़ील्ड भरना अनिवार्य है। कृपया फिर से प्रयास करें।'
            })

        # Generate QR code
        qr_data = f"Name: {name}, Location: {location}, Issue: {issue}"
        qr = qrcode.make(qr_data)
        qr_io = io.BytesIO()
        qr.save(qr_io, format='PNG')
        qr_file = ContentFile(qr_io.getvalue(), f"{name}_qr.png")

        # Save to DB
        complaint = Complaint.objects.create(
            name=name,
            location=location,
            issue=issue,
            photo=photo,
            qr_code=qr_file
        )

        return render(request, 'complaints/success.html', {'complaint': complaint})

    return render(request, 'complaints/form.html')


# ✅ Static Page Views
def home(request):
    return render(request, 'complaints/home.html')

def about_view(request):
    return render(request, 'complaints/about.html')

def report_view(request):
    return render(request, 'complaints/report.html')

def track_complaint_view(request):
    return render(request, 'complaints/trackcomplaint.html')

def dashboard_view(request):
    return render(request, 'complaints/publicDeshBoard.html')

def offline_help_view(request):
    return render(request, 'complaints/offlinehelp.html')

def success_view(request):
    return render(request, "complaints/success.html")


# ✅ User Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, 'यूज़रनेम या पासवर्ड गलत है।')

    return render(request, 'complaints/user.html')  # ✅ Fixed template name


# ✅ User Registration View
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'यूज़रनेम पहले से मौजूद है।')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'रजिस्ट्रेशन सफल हुआ! अब लॉगिन करें।')
            return redirect('login')

    return render(request, 'complaints/register.html')