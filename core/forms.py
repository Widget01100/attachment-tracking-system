from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    UserProfile, Student, Department, UniversitySupervisor, 
    Industry, Organization, AttachmentPeriod, AttachmentApplication,
    LogBook, Evaluation, Document, Notification, Message, Announcement, Report
)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone_number = forms.CharField(max_length=15)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, initial='student')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['registration_number', 'course', 'year_of_study', 'cgpa',
                  'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']
        widgets = {
            'year_of_study': forms.Select(choices=Student.YEAR_CHOICES),
            'cgpa': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '4.0'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['registration_number', 'course', 'year_of_study', 'cgpa',
                  'cv', 'academic_transcript', 'recommendation_letter',
                  'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']
        widgets = {
            'year_of_study': forms.Select(choices=Student.YEAR_CHOICES),
        }

class OrganizationRegistrationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'registration_number', 'company_type', 'industry',
            'physical_address', 'postal_address', 'city', 'county', 'website',
            'contact_person_name', 'contact_person_title', 'contact_email', 'contact_phone', 'alternate_phone',
            'year_established', 'employee_count', 'annual_turnover', 'kra_pin',
            'certificate_of_incorporation', 'kra_pin_certificate', 'business_permit', 'audited_accounts',
            'max_attachment_students', 'provides_stipend', 'stipend_amount',
            'provides_accommodation', 'accommodation_details',
            'has_industry_supervisor', 'industry_supervisor_name', 'industry_supervisor_title',
            'industry_supervisor_email', 'industry_supervisor_phone'
        ]
        widgets = {
            'company_type': forms.Select(choices=Organization.COMPANY_TYPES),
            'year_established': forms.NumberInput(attrs={'min': '1900', 'max': '2026'}),
            'employee_count': forms.NumberInput(attrs={'min': '1'}),
            'annual_turnover': forms.NumberInput(attrs={'step': '0.01'}),
            'max_attachment_students': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
            'stipend_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'physical_address': forms.Textarea(attrs={'rows': 3}),
            'accommodation_details': forms.Textarea(attrs={'rows': 3}),
        }

class OrganizationVerificationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['verification_status', 'rejection_reason']
        widgets = {
            'verification_status': forms.Select(choices=Organization.VERIFICATION_STATUS),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = AttachmentApplication
        fields = [
            'organization', 'attachment_period', 'proposed_start_date', 'proposed_end_date',
            'position_applied', 'motivation_letter', 'introduction_letter'
        ]
        widgets = {
            'proposed_start_date': forms.DateInput(attrs={'type': 'date'}),
            'proposed_end_date': forms.DateInput(attrs={'type': 'date'}),
            'motivation_letter': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'introduction_letter': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('proposed_start_date')
        end_date = cleaned_data.get('proposed_end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data

class LogBookForm(forms.ModelForm):
    class Meta:
        model = LogBook
        fields = [
            'week_number', 'week_start_date', 'week_end_date',
            'monday_activities', 'tuesday_activities', 'wednesday_activities',
            'thursday_activities', 'friday_activities',
            'tasks_completed', 'skills_acquired', 'challenges_faced', 'lessons_learned'
        ]
        widgets = {
            'week_start_date': forms.DateInput(attrs={'type': 'date'}),
            'week_end_date': forms.DateInput(attrs={'type': 'date'}),
            'monday_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities for Monday'}),
            'tuesday_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities for Tuesday'}),
            'wednesday_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities for Wednesday'}),
            'thursday_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities for Thursday'}),
            'friday_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities for Friday'}),
            'tasks_completed': forms.Textarea(attrs={'rows': 3}),
            'skills_acquired': forms.Textarea(attrs={'rows': 3}),
            'challenges_faced': forms.Textarea(attrs={'rows': 3}),
            'lessons_learned': forms.Textarea(attrs={'rows': 3}),
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'evaluation_type', 'punctuality', 'professionalism', 'communication',
            'teamwork', 'initiative', 'technical_knowledge', 'problem_solving',
            'quality_of_work', 'productivity', 'strengths', 'areas_for_improvement',
            'general_comments', 'recommendations', 'would_recommend'
        ]
        widgets = {
            'evaluation_type': forms.Select(choices=Evaluation.EVAL_TYPES),
            'punctuality': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'professionalism': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'communication': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'teamwork': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'initiative': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'technical_knowledge': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'problem_solving': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'quality_of_work': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'productivity': forms.NumberInput(attrs={'min': '1', 'max': '10', 'step': '1'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 3}),
            'general_comments': forms.Textarea(attrs={'rows': 3}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'body': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Type your message here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter recipients based on user type and permissions
            if user.is_superuser or user.profile.user_type == 'coordinator':
                self.fields['recipient'].queryset = User.objects.filter(is_active=True)
            elif user.profile.user_type == 'university_supervisor':
                self.fields['recipient'].queryset = User.objects.filter(
                    profile__user_type='student'
                ).filter(is_active=True)
            elif user.profile.user_type == 'student':
                self.fields['recipient'].queryset = User.objects.filter(
                    profile__user_type__in=['university_supervisor', 'coordinator']
                ).filter(is_active=True)

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'target_roles', 'publish_date', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'priority': forms.Select(choices=Announcement.PRIORITY_CHOICES, attrs={'class': 'form-select'}),
            'target_roles': forms.CheckboxSelectMultiple(choices=UserProfile.USER_TYPES),
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class AttachmentPeriodForm(forms.ModelForm):
    class Meta:
        model = AttachmentPeriod
        fields = ['name', 'start_date', 'end_date', 'application_deadline', 'year', 'semester', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2030'}),
            'semester': forms.Select(choices=[(1, 'Semester 1'), (2, 'Semester 2'), (3, 'Semester 3')], 
                                    attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'title', 'description', 'file']
        widgets = {
            'document_type': forms.Select(choices=Document.DOCUMENT_TYPES, attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.png'}),
        }

class ReportGenerationForm(forms.Form):
    REPORT_TYPES = [
        ('student_progress', 'Student Progress Report'),
        ('organization_performance', 'Organization Performance'),
        ('supervisor_evaluations', 'Supervisor Evaluations'),
        ('placement_statistics', 'Placement Statistics'),
        ('compliance_report', 'Compliance Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    report_type = forms.ChoiceField(choices=REPORT_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    format = forms.ChoiceField(choices=FORMAT_CHOICES, initial='pdf', widget=forms.Select(attrs={'class': 'form-select'}))
    include_charts = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    detailed = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class SupervisorAssignmentForm(forms.Form):
    supervisor = forms.ModelChoiceField(
        queryset=UniversitySupervisor.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(current_status='on_attachment'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'})
    )
    
    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['supervisor'].queryset = UniversitySupervisor.objects.filter(department=department)
