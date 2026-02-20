from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StudentProfile, Organization, Attachment, LogbookEntry, Evaluation

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['registration_number', 'course', 'university', 'phone', 'year_of_study']
        widgets = {
            'year_of_study': forms.NumberInput(attrs={'min': 1, 'max': 4})
        }

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['organization', 'start_date', 'end_date', 'application_letter']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data

class LogbookEntryForm(forms.ModelForm):
    class Meta:
        model = LogbookEntry
        fields = ['entry_date', 'activities', 'skills_learned', 'challenges']
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'activities': forms.Textarea(attrs={'rows': 4}),
            'skills_learned': forms.Textarea(attrs={'rows': 3}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['eval_type', 'punctuality', 'professionalism', 'technical_skills', 
                  'communication', 'teamwork', 'comments', 'recommendations']
        widgets = {
            'punctuality': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'professionalism': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'technical_skills': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'communication': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'teamwork': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'comments': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
        }

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'industry', 'location', 'contact_person', 'contact_email', 'contact_phone']
