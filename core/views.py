from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import date
from .models import *
from .forms import *

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = StudentProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = StudentProfileForm()
    
    return render(request, 'core/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
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
        context['total_students'] = StudentProfile.objects.count()
        context['total_organizations'] = Organization.objects.count()
        context['pending_attachments'] = Attachment.objects.filter(status='pending').count()
        context['active_attachments'] = Attachment.objects.filter(status='active').count()
        context['recent_attachments'] = Attachment.objects.all()[:5]
        
    elif hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        context['attachments'] = Attachment.objects.filter(student=student)
        context['active_attachment'] = Attachment.objects.filter(
            student=student, 
            status='active'
        ).first()
        context['notifications'] = Notification.objects.filter(user=request.user, is_read=False)[:5]
        
    else:
        context['supervised_attachments'] = Attachment.objects.filter(university_supervisor=request.user)
        context['pending_evaluations'] = Attachment.objects.filter(
            university_supervisor=request.user,
            status='active'
        ).count()
    
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        if hasattr(request.user, 'student_profile'):
            form = StudentProfileForm(request.POST, instance=request.user.student_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
    else:
        if hasattr(request.user, 'student_profile'):
            form = StudentProfileForm(instance=request.user.student_profile)
        else:
            form = None
    
    return render(request, 'core/profile.html', {'form': form})

@login_required
def apply_attachment(request):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'Only students can apply for attachments.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AttachmentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.student = request.user.student_profile
            attachment.status = 'pending'
            attachment.save()
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('dashboard')
    else:
        form = AttachmentApplicationForm()
    
    organizations = Organization.objects.filter(is_approved=True)
    
    return render(request, 'core/apply_attachment.html', {
        'form': form,
        'organizations': organizations
    })

@login_required
def logbook(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    
    if request.user.is_superuser or attachment.student.user == request.user or attachment.university_supervisor == request.user:
        
        if request.method == 'POST' and attachment.student.user == request.user:
            form = LogbookEntryForm(request.POST)
            if form.is_valid():
                entry = form.save(commit=False)
                entry.attachment = attachment
                entry.save()
                messages.success(request, 'Log entry added successfully!')
                return redirect('logbook', attachment_id=attachment.id)
        else:
            form = LogbookEntryForm()
        
        entries = LogbookEntry.objects.filter(attachment=attachment)
        return render(request, 'core/logbook.html', {
            'attachment': attachment,
            'entries': entries,
            'form': form if attachment.student.user == request.user else None
        })
    else:
        messages.error(request, 'You do not have permission to view this logbook.')
        return redirect('dashboard')

@login_required
def evaluate(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    
    if request.user.is_superuser or attachment.university_supervisor == request.user:
        
        if request.method == 'POST':
            form = EvaluationForm(request.POST)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.attachment = attachment
                evaluation.evaluator = request.user
                evaluation.save()
                
                messages.success(request, 'Evaluation submitted successfully!')
                return redirect('dashboard')
        else:
            form = EvaluationForm()
        
        return render(request, 'core/evaluate.html', {
            'attachment': attachment,
            'form': form
        })
    else:
        messages.error(request, 'You are not authorized to evaluate this attachment.')
        return redirect('dashboard')
