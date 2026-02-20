from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    year_of_study = models.IntegerField(default=2)
    
    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name()}"

class Organization(models.Model):
    name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Attachment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attachments')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_attachments')
    organization_supervisor = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_letter = models.FileField(upload_to='documents/applications/', blank=True, null=True)
    offer_letter = models.FileField(upload_to='documents/offers/', blank=True, null=True)
    report = models.FileField(upload_to='documents/reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - {self.organization} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class LogbookEntry(models.Model):
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, related_name='logbook_entries')
    entry_date = models.DateField()
    activities = models.TextField()
    skills_learned = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    supervisor_comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Entry for {self.attachment.student} on {self.entry_date}"
    
    class Meta:
        ordering = ['-entry_date']
        unique_together = ['attachment', 'entry_date']

class Evaluation(models.Model):
    EVAL_TYPES = [
        ('midterm', 'Mid-term Evaluation'),
        ('final', 'Final Evaluation'),
    ]
    
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE)
    eval_type = models.CharField(max_length=20, choices=EVAL_TYPES)
    
    # Evaluation criteria
    punctuality = models.IntegerField(help_text="Score 1-10")
    professionalism = models.IntegerField(help_text="Score 1-10")
    technical_skills = models.IntegerField(help_text="Score 1-10")
    communication = models.IntegerField(help_text="Score 1-10")
    teamwork = models.IntegerField(help_text="Score 1-10")
    
    comments = models.TextField()
    recommendations = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def total_score(self):
        return (self.punctuality + self.professionalism + self.technical_skills + 
                self.communication + self.teamwork) / 5
    
    def __str__(self):
        return f"{self.eval_type} - {self.attachment.student}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

# Signal to create notification when attachment status changes
@receiver(post_save, sender=Attachment)
def attachment_status_changed(sender, instance, created, **kwargs):
    if not created:
        # Status changed
        Notification.objects.create(
            user=instance.student.user,
            title="Attachment Status Updated",
            message=f"Your attachment application status has been updated to: {instance.get_status_display()}",
            link="/dashboard/"
        )
