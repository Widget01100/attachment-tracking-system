from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from .models import *
from .forms import *

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                user_type=user_form.cleaned_data.get('user_type', 'student'),
                phone_number=user_form.cleaned_data.get('phone_number', '')
            )
            
            # If student, create student profile
            if profile.user_type == 'student':
                student_form = StudentRegistrationForm(request.POST)
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user_profile = profile
                    student.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
    
    return render(request, 'core/register.html', {
        'user_form': user_form
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    context = {}
    
    if request.user.is_superuser:
        # Admin dashboard
        context['total_students'] = Student.objects.count()
        context['total_organizations'] = Organization.objects.count()
        context['pending_applications'] = AttachmentApplication.objects.filter(status='pending').count()
        context['active_attachments'] = AttachmentApplication.objects.filter(status='ongoing').count()
        context['recent_applications'] = AttachmentApplication.objects.all()[:5]
        context['verified_organizations'] = Organization.objects.filter(verification_status='verified').count()
        context['new_students_this_month'] = Student.objects.filter(
            created_at__month=timezone.now().month
        ).count()
        
    elif hasattr(request.user, 'profile') and request.user.profile.user_type == 'student':
        # Student dashboard
        try:
            student = Student.objects.get(user_profile=request.user.profile)
            context['student_profile'] = student
            context['student_applications'] = AttachmentApplication.objects.filter(student=student)
            context['total_applications'] = context['student_applications'].count()
            context['approved_applications'] = context['student_applications'].filter(status='approved').count()
            context['pending_applications'] = context['student_applications'].filter(status='pending').count()
        except Student.DoesNotExist:
            messages.warning(request, 'Please complete your student profile.')
            return redirect('profile')
        
    elif hasattr(request.user, 'profile') and request.user.profile.user_type == 'university_supervisor':
        # Supervisor dashboard
        try:
            supervisor = UniversitySupervisor.objects.get(user_profile=request.user.profile)
            context['supervised_students'] = AttachmentApplication.objects.filter(
                assigned_supervisor=supervisor,
                status='ongoing'
            ).select_related('student__user_profile__user')
            context['assigned_students'] = context['supervised_students'].count()
            context['pending_evaluations'] = Evaluation.objects.filter(
                application__assigned_supervisor=supervisor,
                application__status='ongoing'
            ).count()
        except UniversitySupervisor.DoesNotExist:
            messages.warning(request, 'Please complete your supervisor profile.')
            return redirect('profile')
    
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'core/profile.html')

# Applications
def applications_list(request):
    return render(request, 'core/applications_list.html')

def application_detail(request, app_id):
    return render(request, 'core/application_detail.html')

def withdraw_application(request, app_id):
    return redirect('applications')

@login_required
def apply_attachment(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.user_type == 'student'):
        messages.error(request, 'Only students can apply for attachments.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AttachmentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = Student.objects.get(user_profile=request.user.profile)
            application.status = 'submitted'
            application.submitted_at = timezone.now()
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('applications')
    else:
        form = AttachmentApplicationForm()
    
    # Get active attachment periods and organizations for the form
    active_periods = AttachmentPeriod.objects.filter(is_active=True)
    organizations = Organization.objects.filter(verification_status='verified')
    
    return render(request, 'core/apply_attachment.html', {
        'form': form,
        'active_periods': active_periods,
        'organizations': organizations
    })

# Organizations
def organizations_list(request):
    organizations = Organization.objects.all()
    return render(request, 'core/organizations_list.html', {'organizations': organizations})

def organization_detail(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    return render(request, 'core/organization_detail.html', {'organization': organization})

def register_organization(request):
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.verification_status = 'pending'
            organization.save()
            messages.success(request, 'Organization registered successfully! Pending verification.')
            return redirect('organizations')
    else:
        form = OrganizationRegistrationForm()
    
    return render(request, 'core/register_organization.html', {'form': form})

@login_required
def verify_organization(request, org_id):
    if not (request.user.is_superuser or request.user.profile.user_type == 'coordinator'):
        messages.error(request, 'You are not authorized to verify organizations.')
        return redirect('organizations')
    
    organization = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        form = OrganizationVerificationForm(request.POST, instance=organization)
        if form.is_valid():
            org = form.save(commit=False)
            org.verified_by = request.user
            org.verified_at = timezone.now()
            org.save()
            messages.success(request, f'Organization {org.verification_status}')
            return redirect('organization_detail', org_id=org.id)
    else:
        form = OrganizationVerificationForm(instance=organization)
    
    return render(request, 'core/verify_organization.html', {
        'form': form,
        'organization': organization
    })

# Logbook
@login_required
def logbook(request, app_id):
    application = get_object_or_404(AttachmentApplication, id=app_id)
    
    # Check permissions
    if not (request.user.is_superuser or 
            request.user.profile.user_type == 'university_supervisor' or
            (request.user.profile.user_type == 'student' and 
             application.student.user_profile.user == request.user)):
        messages.error(request, 'You do not have permission to view this logbook.')
        return redirect('dashboard')
    
    logbooks = LogBook.objects.filter(application=application)
    return render(request, 'core/logbook.html', {
        'application': application,
        'logbooks': logbooks
    })

def logbook_entry(request, app_id, week):
    return render(request, 'core/logbook_entry.html')

def approve_logbook(request, entry_id):
    return redirect('dashboard')

# Evaluations
@login_required
def evaluate(request, app_id):
    application = get_object_or_404(AttachmentApplication, id=app_id)
    
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.application = application
            evaluation.evaluator = request.user
            evaluation.save()
            messages.success(request, 'Evaluation submitted successfully!')
            return redirect('evaluations_list')
    else:
        form = EvaluationForm()
    
    return render(request, 'core/evaluate.html', {
        'form': form,
        'application': application
    })

def evaluations_list(request):
    return render(request, 'core/evaluations_list.html')

def evaluation_detail(request, eval_id):
    return render(request, 'core/evaluation_detail.html')

# Messaging
def messages_list(request):
    return render(request, 'core/messages_list.html')

def message_detail(request, message_id):
    return render(request, 'core/message_detail.html')

@login_required
def new_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messages_list')
    else:
        form = MessageForm(user=request.user)
    
    return render(request, 'core/new_message.html', {'form': form})

def reply_message(request, message_id):
    return redirect('messages')

# Notifications
def notifications_list(request):
    return render(request, 'core/notifications_list.html')

def mark_notification_read(request, notif_id):
    return redirect('notifications')

def mark_all_read(request):
    return redirect('notifications')

def unread_notifications_count(request):
    return JsonResponse({'count': 0})

def unread_messages_count(request):
    return JsonResponse({'count': 0})

# Reports
def reports_list(request):
    return render(request, 'core/reports_list.html')

def generate_report(request):
    return render(request, 'core/generate_report.html')

def download_report(request, report_id):
    return redirect('reports')

# Admin/Coordinator
def students_list(request):
    return render(request, 'core/students_list.html')

def student_detail(request, student_id):
    return render(request, 'core/student_detail.html')

def message_student(request, student_id):
    return redirect('new_message')

def supervisors_list(request):
    return render(request, 'core/supervisors_list.html')

def departments_list(request):
    return render(request, 'core/departments_list.html')

def attachment_periods(request):
    return render(request, 'core/attachment_periods.html')

def create_attachment_period(request):
    return render(request, 'core/create_attachment_period.html')

# Announcements
def announcements_list(request):
    return render(request, 'core/announcements_list.html')

def create_announcement(request):
    return render(request, 'core/create_announcement.html')

def announcement_detail(request, ann_id):
    return render(request, 'core/announcement_detail.html')
