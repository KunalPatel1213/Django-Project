from django.shortcuts import render

# होम पेज व्यू
def home(request):
    return render(request, 'page1/home.html')
def about_view(request):
    return render(request, 'page1/about.html')
def report_view(request):
    return render(request, 'page1/report.html')
def track_complaint_view(request):
    return render(request, 'page1/trackcomplaint.html')
def dashboard_view(request):
    return render(request, 'page1/publicDeshBoard.html')
def offline_help_view(request):
    return render(request, 'page1/offlinehelp.html')

