from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from datetime import timedelta
import os

# ========== USER MANAGEMENT ==========

class UserProfile(models.Model):
    """Extended user profile for all users"""
    USER_TYPES = [
        ('student', 'Student'),
        ('university_supervisor', 'University Supervisor'),
        ('industry_supervisor', 'Industry Supervisor'),
        ('coordinator', 'Attachment Coordinator'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=30, choices=USER_TYPES, default='student')
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    id_number = models.CharField(max_length=20, blank=True, help_text="National ID/Passport")
    alternate_email = models.EmailField(blank=True)
    postal_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user_type}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

# ========== ACADEMIC STRUCTURE ==========

class Faculty(models.Model):
    """University faculties/schools"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    dean_name = models.CharField(max_length=200)
    dean_email = models.EmailField()
    dean_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Department(models.Model):
    """University departments"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    hod_name = models.CharField(max_length=200)
    hod_email = models.EmailField()
    hod_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Course(models.Model):
    """Academic programs/courses"""
    LEVEL_CHOICES = [
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('degree', 'Bachelor\'s Degree'),
        ('masters', 'Master\'s Degree'),
        ('phd', 'PhD'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration_years = models.IntegerField(default=4)
    requires_attachment = models.BooleanField(default=True)
    attachment_semester = models.IntegerField(default=3, help_text="Semester when attachment is done")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class AcademicYear(models.Model):
    """Academic years (e.g., 2025/2026)"""
    name = models.CharField(max_length=20, unique=True)  # e.g., "2025/2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date']

class Semester(models.Model):
    """Academic semesters"""
    SEMESTER_CHOICES = [(1, 'Semester 1'), (2, 'Semester 2'), (3, 'Semester 3')]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.IntegerField(choices=SEMESTER_CHOICES)
    name = models.CharField(max_length=50)  # e.g., "Semester 1 2025/2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['academic_year', 'semester_number']
        ordering = ['academic_year', 'semester_number']

# ========== STUDENT MANAGEMENT ==========

class Student(models.Model):
    """Detailed student information"""
    YEAR_CHOICES = [(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_attachment', 'On Attachment'),
        ('completed', 'Completed'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
        ('probation', 'Academic Probation'),
    ]
    
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='student_details')
    registration_number = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    current_year = models.IntegerField(choices=YEAR_CHOICES, default=2)
    current_semester = models.IntegerField(default=1)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Academic information
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    credits_completed = models.IntegerField(default=0)
    credits_required = models.IntegerField(default=160)
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    
    # Contact information
    personal_email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    physical_address = models.TextField(blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_alternate = models.CharField(max_length=15, blank=True)
    
    # Documents
    cv = models.FileField(
        upload_to='documents/students/cv/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    academic_transcript = models.FileField(
        upload_to='documents/students/transcripts/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    recommendation_letter = models.FileField(
        upload_to='documents/students/recommendations/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    passport_photo = models.ImageField(upload_to='documents/students/photos/', blank=True, null=True)
    good_conduct_certificate = models.FileField(
        upload_to='documents/students/conduct/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    insurance_cover = models.FileField(
        upload_to='documents/students/insurance/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # Bank details (for stipend)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_swift_code = models.CharField(max_length=20, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_students')
    
    def __str__(self):
        return f"{self.registration_number} - {self.user_profile.user.get_full_name()}"
    
    class Meta:
        ordering = ['registration_number']
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['current_status']),
        ]

# ========== UNIVERSITY SUPERVISOR MANAGEMENT ==========

class UniversitySupervisor(models.Model):
    """Lecturers/supervisors from the university"""
    TITLE_CHOICES = [
        ('prof', 'Professor'),
        ('dr', 'Dr.'),
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
    ]
    
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='supervisor_details')
    employee_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='supervisors')
    designation = models.CharField(max_length=100)  # Lecturer, Senior Lecturer, etc.
    specialization = models.TextField()
    
    # Employment details
    employment_date = models.DateField()
    is_permanent = models.BooleanField(default=True)
    max_students = models.IntegerField(default=10, help_text="Maximum students they can supervise")
    current_students = models.IntegerField(default=0)
    
    # Contact
    office_location = models.CharField(max_length=200, blank=True)
    office_phone = models.CharField(max_length=15, blank=True)
    
    # Qualifications
    highest_qualification = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_completed = models.IntegerField(null=True, blank=True)
    
    # Documents
    cv = models.FileField(upload_to='documents/supervisors/cv/', blank=True, null=True)
    academic_certificates = models.FileField(upload_to='documents/supervisors/certificates/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_title_display()} {self.user_profile.user.get_full_name()} - {self.department.code}"
    
    def can_take_more_students(self):
        return self.current_students < self.max_students

# ========== INDUSTRY/ORGANIZATION MANAGEMENT ==========

class Industry(models.Model):
    """Industry sectors"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Industries"
        ordering = ['name']

class Organization(models.Model):
    """Companies/Organizations that offer attachments"""
    COMPANY_TYPES = [
        ('private', 'Private Limited Company'),
        ('public', 'Public Limited Company'),
        ('ngo', 'Non-Governmental Organization'),
        ('government', 'Government Agency/Parastatal'),
        ('international', 'International Organization'),
        ('sme', 'Small & Medium Enterprise'),
        ('startup', 'Startup'),
        ('partnership', 'Partnership'),
        ('sole', 'Sole Proprietorship'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    
    # Basic information
    name = models.CharField(max_length=300)
    registration_number = models.CharField(max_length=100, unique=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='organizations')
    
    # Address information
    physical_address = models.TextField()
    postal_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    website = models.URLField(blank=True)
    
    # Primary contact
    contact_person_name = models.CharField(max_length=200)
    contact_person_title = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    contact_person_id = models.CharField(max_length=20, blank=True, help_text="ID/Passport number of contact person")
    
    # HR contact (if different)
    hr_name = models.CharField(max_length=200, blank=True)
    hr_email = models.EmailField(blank=True)
    hr_phone = models.CharField(max_length=15, blank=True)
    
    # Company details
    year_established = models.IntegerField()
    employee_count = models.IntegerField()
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    kra_pin = models.CharField(max_length=20)
    
    # Verification documents
    certificate_of_incorporation = models.FileField(
        upload_to='documents/organizations/incorporation/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    kra_pin_certificate = models.FileField(
        upload_to='documents/organizations/kra/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    business_permit = models.FileField(
        upload_to='documents/organizations/permits/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    audited_accounts = models.FileField(
        upload_to='documents/organizations/accounts/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    director_id = models.FileField(
        upload_to='documents/organizations/directors/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # Status
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_organizations')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    verification_expiry = models.DateField(null=True, blank=True, help_text="Date when verification expires")
    
    # Attachment capacity
    max_attachment_students = models.IntegerField(default=5)
    current_attachment_students = models.IntegerField(default=0)
    provides_stipend = models.BooleanField(default=False)
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stipend_payment_schedule = models.CharField(max_length=100, blank=True, help_text="e.g., Monthly, End of attachment")
    provides_accommodation = models.BooleanField(default=False)
    accommodation_details = models.TextField(blank=True)
    provides_meals = models.BooleanField(default=False)
    provides_transport = models.BooleanField(default=False)
    provides_ppe = models.BooleanField(default=False, help_text="Personal Protective Equipment")
    
    # Supervision
    has_industry_supervisor = models.BooleanField(default=True)
    industry_supervisor_name = models.CharField(max_length=200, blank=True)
    industry_supervisor_title = models.CharField(max_length=100, blank=True)
    industry_supervisor_email = models.EmailField(blank=True)
    industry_supervisor_phone = models.CharField(max_length=15, blank=True)
    industry_supervisor_id = models.CharField(max_length=20, blank=True)
    
    # Departments/Sections available for attachment
    available_departments = models.TextField(help_text="List departments separated by commas", blank=True)
    
    # Historical data
    total_students_hosted = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_organizations')
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"
    
    def has_capacity(self):
        return self.current_attachment_students < self.max_attachment_students
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['verification_status']),
            models.Index(fields=['name']),
        ]

class OrganizationContact(models.Model):
    """Additional contacts within an organization"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='additional_contacts')
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    is_primary = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"

# ========== ATTACHMENT PERIOD MANAGEMENT ==========

class AttachmentPeriod(models.Model):
    """Defines attachment periods/semesters"""
    name = models.CharField(max_length=100)  # e.g., "May-August 2026"
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='attachment_periods')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='attachment_periods', null=True, blank=True)
    
    # Dates
    application_start_date = models.DateField()
    application_deadline = models.DateField()
    placement_deadline = models.DateField(help_text="Deadline for securing placement")
    start_date = models.DateField(help_text="When attachment should start")
    end_date = models.DateField(help_text="When attachment should end")
    report_submission_deadline = models.DateField(help_text="Deadline for submitting final report")
    
    # Duration
    duration_weeks = models.IntegerField(default=12, help_text="Standard duration in weeks")
    min_duration_weeks = models.IntegerField(default=8)
    max_duration_weeks = models.IntegerField(default=16)
    
    # Capacity
    max_students = models.IntegerField(default=500, help_text="Maximum students for this period")
    current_applications = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=False)
    is_open_for_applications = models.BooleanField(default=True)
    is_open_for_placements = models.BooleanField(default=True)
    
    # Requirements
    required_documents = models.JSONField(default=list, help_text="List of required document types")
    min_cgpa_required = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    min_year_of_study = models.IntegerField(default=3)
    
    # Fees
    attachment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    admin_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def is_application_open(self):
        today = timezone.now().date()
        return self.application_start_date <= today <= self.application_deadline
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['application_deadline']),
        ]

# ========== ATTACHMENT APPLICATION WORKFLOW ==========

class AttachmentApplication(models.Model):
    """Student applications for attachment"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('documents_verified', 'Documents Verified'),
        ('department_review', 'Under Department Review'),
        ('coordinator_review', 'Under Coordinator Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('placed', 'Placed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    # Core relationships
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='applications')
    attachment_period = models.ForeignKey(AttachmentPeriod, on_delete=models.CASCADE, related_name='applications')
    
    # Application details
    proposed_start_date = models.DateField()
    proposed_end_date = models.DateField()
    position_applied = models.CharField(max_length=200)
    department_section = models.CharField(max_length=200, blank=True, help_text="Specific department within organization")
    
    # Motivation
    motivation_statement = models.TextField(help_text="Why you want this attachment")
    what_you_hope_to_learn = models.TextField(blank=True)
    relevant_skills = models.TextField(blank=True)
    previous_experience = models.TextField(blank=True)
    
    # Documents
    motivation_letter = models.FileField(
        upload_to='documents/applications/motivation/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    introduction_letter = models.FileField(
        upload_to='documents/applications/introduction/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    cv_uploaded = models.FileField(
        upload_to='documents/applications/cv/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    acceptance_letter = models.FileField(
        upload_to='documents/applications/acceptance/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    offer_letter = models.FileField(
        upload_to='documents/applications/offer/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    documents_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Department approval
    department_approved_by = models.ForeignKey(
        UniversitySupervisor, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='department_approved_applications'
    )
    department_approved_at = models.DateTimeField(null=True, blank=True)
    department_comments = models.TextField(blank=True)
    
    # Coordinator approval
    coordinator_approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='coordinator_approved_applications'
    )
    coordinator_approved_at = models.DateTimeField(null=True, blank=True)
    coordinator_comments = models.TextField(blank=True)
    
    # Rejection
    rejection_reason = models.TextField(blank=True)
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_applications')
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_stage = models.CharField(max_length=50, blank=True, help_text="Stage at which rejected")
    
    # Assignment
    assigned_supervisor = models.ForeignKey(
        UniversitySupervisor, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='assigned_applications'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Industry supervisor details (if not the primary contact)
    industry_supervisor_name = models.CharField(max_length=200, blank=True)
    industry_supervisor_title = models.CharField(max_length=100, blank=True)
    industry_supervisor_email = models.EmailField(blank=True)
    industry_supervisor_phone = models.CharField(max_length=15, blank=True)
    
    # Stipend information
    stipend_agreed = models.BooleanField(default=False)
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stipend_currency = models.CharField(max_length=3, default='KES')
    stipend_notes = models.TextField(blank=True)
    
    # Accommodation
    accommodation_provided = models.BooleanField(default=False)
    accommodation_details = models.TextField(blank=True)
    
    # Progress tracking
    current_week = models.IntegerField(default=0)
    total_weeks = models.IntegerField(default=12)
    progress_percentage = models.IntegerField(default=0)
    
    # Marks (from evaluation)
    industry_supervisor_marks = models.IntegerField(null=True, blank=True)
    university_supervisor_marks = models.IntegerField(null=True, blank=True)
    report_marks = models.IntegerField(null=True, blank=True)
    logbook_presentation_marks = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True, help_text="A, B, C, etc.")
    
    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_certificate = models.FileField(
        upload_to='documents/applications/certificates/',
        blank=True, null=True
    )
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_applications')
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.organization.name} ({self.status})"
    
    def calculate_progress(self):
        """Calculate progress percentage based on weeks completed"""
        if self.status == 'ongoing' and self.start_date and self.end_date:
            total_days = (self.end_date - self.start_date).days
            elapsed_days = (timezone.now().date() - self.start_date).days
            if total_days > 0:
                progress = min(100, int((elapsed_days / total_days) * 100))
                self.progress_percentage = progress
                self.current_week = int((elapsed_days / 7) + 1)
                return progress
        return 0
    
    def calculate_total_marks(self):
        """Calculate total marks from all components"""
        total = 0
        count = 0
        if self.industry_supervisor_marks:
            total += self.industry_supervisor_marks
            count += 1
        if self.university_supervisor_marks:
            total += self.university_supervisor_marks
            count += 1
        if self.report_marks:
            total += self.report_marks
            count += 1
        if self.logbook_presentation_marks:
            total += self.logbook_presentation_marks
            count += 1
        
        if count > 0:
            self.total_marks = total
            return total
        return None
    
    def calculate_grade(self):
        """Calculate grade based on total marks"""
        if self.total_marks:
            if self.total_marks >= 70:
                self.grade = 'A'
            elif self.total_marks >= 60:
                self.grade = 'B'
            elif self.total_marks >= 50:
                self.grade = 'C'
            elif self.total_marks >= 40:
                self.grade = 'D'
            else:
                self.grade = 'F'
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['organization', 'status']),
        ]
        unique_together = ['student', 'attachment_period']  # One application per period

# ========== LOGBOOK SYSTEM ==========

class LogBook(models.Model):
    """Weekly logbook entries"""
    application = models.ForeignKey(AttachmentApplication, on_delete=models.CASCADE, related_name='logbooks')
    week_number = models.IntegerField()
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    
    # Daily activities
    monday_activities = models.TextField(blank=True)
    monday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    tuesday_activities = models.TextField(blank=True)
    tuesday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    wednesday_activities = models.TextField(blank=True)
    wednesday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    thursday_activities = models.TextField(blank=True)
    thursday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    friday_activities = models.TextField(blank=True)
    friday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    saturday_activities = models.TextField(blank=True)
    saturday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    sunday_activities = models.TextField(blank=True)
    sunday_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    
    # Weekly summary
    tasks_completed = models.TextField()
    skills_acquired = models.TextField()
    challenges_faced = models.TextField()
    lessons_learned = models.TextField()
    plans_for_next_week = models.TextField(blank=True)
    
    # Supervisor comments
    industry_supervisor_comments = models.TextField(blank=True)
    industry_supervisor_approved = models.BooleanField(default=False)
    industry_supervisor_approved_at = models.DateTimeField(null=True, blank=True)
    industry_supervisor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    university_supervisor_comments = models.TextField(blank=True)
    university_supervisor_approved = models.BooleanField(default=False)
    university_supervisor_approved_at = models.DateTimeField(null=True, blank=True)
    
    # Attachments
    supporting_documents = models.FileField(
        upload_to='logbook/attachments/',
        blank=True, null=True
    )
    photos = models.ImageField(upload_to='logbook/photos/', blank=True, null=True)
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"Week {self.week_number} - {self.application.student.registration_number}"
    
    def total_hours_week(self):
        """Calculate total hours for the week"""
        return (self.monday_hours + self.tuesday_hours + self.wednesday_hours +
                self.thursday_hours + self.friday_hours + self.saturday_hours +
                self.sunday_hours)
    
    class Meta:
        ordering = ['week_number']
        unique_together = ['application', 'week_number']

class LogBookComment(models.Model):
    """Comments on logbook entries"""
    logbook = models.ForeignKey(LogBook, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_private = models.BooleanField(default=False, help_text="Only visible to supervisors")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"

# ========== EVALUATION SYSTEM ==========

class Evaluation(models.Model):
    """Supervisor evaluations"""
    EVAL_TYPES = [
        ('mid_term', 'Mid-Term Evaluation'),
        ('final', 'Final Evaluation'),
    ]
    
    application = models.ForeignKey(AttachmentApplication, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation_type = models.CharField(max_length=20, choices=EVAL_TYPES)
    
    # SECTION A: Professional Competencies (50%)
    # Work habits (20%)
    punctuality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Arrives on time, meets deadlines"
    )
    reliability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Can be depended on to complete tasks"
    )
    initiative = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Self-starter, proactive approach"
    )
    
    # Interpersonal skills (20%)
    teamwork = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Works well with others"
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Clear verbal and written communication"
    )
    professionalism = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Professional demeanor and appearance"
    )
    
    # SECTION B: Technical Competencies (50%)
    # Knowledge application (25%)
    technical_knowledge = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Applies academic knowledge to tasks"
    )
    problem_solving = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Ability to identify and solve problems"
    )
    
    # Work quality (25%)
    quality_of_work = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Accuracy and thoroughness"
    )
    productivity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Volume of work produced"
    )
    
    # SECTION C: Comments
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    general_comments = models.TextField()
    recommendations = models.TextField(blank=True)
    
    # Overall
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    would_recommend = models.BooleanField(default=True)
    recommend_for_employment = models.BooleanField(default=False)
    
    # Evaluation meeting
    evaluation_date = models.DateField(auto_now_add=True)
    meeting_conducted = models.BooleanField(default=True)
    meeting_notes = models.TextField(blank=True)
    
    # Signatures
    evaluator_signature = models.ImageField(upload_to='signatures/evaluations/', blank=True, null=True)
    student_acknowledged = models.BooleanField(default=False)
    student_acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # System fields
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_overall(self):
        """Calculate overall score according to weighting"""
        # Professional competencies (50%)
        professional_avg = (
            self.punctuality + self.reliability + self.initiative +
            self.teamwork + self.communication + self.professionalism
        ) / 6 * 5  # Scale to 50
        
        # Technical competencies (50%)
        technical_avg = (
            self.technical_knowledge + self.problem_solving +
            self.quality_of_work + self.productivity
        ) / 4 * 5  # Scale to 50
        
        self.overall_score = professional_avg + technical_avg
        return self.overall_score
    
    def save(self, *args, **kwargs):
        self.calculate_overall()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.evaluation_type} - {self.application.student.registration_number} - {self.overall_score}%"

# ========== DOCUMENT MANAGEMENT ==========

class Document(models.Model):
    """Document management system"""
    DOCUMENT_TYPES = [
        ('application_letter', 'Application Letter'),
        ('introduction_letter', 'Introduction Letter'),
        ('acceptance_letter', 'Acceptance Letter'),
        ('offer_letter', 'Offer Letter'),
        ('logbook', 'Logbook'),
        ('evaluation', 'Evaluation'),
        ('report', 'Report'),
        ('transcript', 'Academic Transcript'),
        ('recommendation', 'Recommendation Letter'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    application = models.ForeignKey(AttachmentApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png'])]
    )
    file_size = models.IntegerField(help_text="File size in bytes", blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.application.student.registration_number}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

# ========== NOTIFICATION SYSTEM ==========

class Notification(models.Model):
    """Notification system"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Alert'),
        ('reminder', 'Reminder'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

# ========== MESSAGING SYSTEM ==========

class Message(models.Model):
    """Internal messaging system"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    # Attachments
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived_by_sender = models.BooleanField(default=False)
    is_archived_by_recipient = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)
    
    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    # Priority
    is_urgent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject
    
    class Meta:
        ordering = ['-created_at']

# ========== ANNOUNCEMENT SYSTEM ==========

class Announcement(models.Model):
    """System-wide announcements"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Targeting
    target_user_types = models.JSONField(default=list, help_text="List of user types to target")  # Empty list means all
    target_departments = models.JSONField(default=list, help_text="List of department IDs")  # Empty list means all
    target_years = models.JSONField(default=list, help_text="List of years of study")  # For students
    
    # Schedule
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    
    # Display options
    show_as_popup = models.BooleanField(default=False)
    requires_acknowledgment = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Tracking
    view_count = models.IntegerField(default=0)
    acknowledgment_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def is_published(self):
        now = timezone.now()
        return self.publish_date <= now <= self.expiry_date
    
    class Meta:
        ordering = ['-publish_date']

class AnnouncementAcknowledgment(models.Model):
    """Track which users have acknowledged announcements"""
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='acknowledgments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        unique_together = ['announcement', 'user']

# ========== REPORT SYSTEM ==========

class Report(models.Model):
    """Generated reports"""
    REPORT_TYPES = [
        ('student_progress', 'Student Progress Report'),
        ('organization_performance', 'Organization Performance'),
        ('supervisor_evaluations', 'Supervisor Evaluations'),
        ('placement_statistics', 'Placement Statistics'),
        ('compliance_report', 'Compliance Report'),
        ('financial_report', 'Financial Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    parameters = models.JSONField(default=dict, help_text="Report parameters used")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Status
    is_ready = models.BooleanField(default=False)
    generation_time = models.FloatField(blank=True, null=True, help_text="Time taken in seconds")
    error_message = models.TextField(blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    access_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.date()}"
    
    class Meta:
        ordering = ['-generated_at']

# ========== AUDIT LOG ==========

class AuditLog(models.Model):
    """Track all important actions in the system"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('upload', 'Upload'),
        ('download', 'Download'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    
    # Changes
    changes = models.JSONField(default=dict, blank=True)
    
    # IP and user agent
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action_type} - {self.model_name}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type']),
        ]

# ========== SIGNALS FOR AUTOMATION ==========

@receiver(post_save, sender=AttachmentApplication)
def create_application_notifications(sender, instance, created, **kwargs):
    """Create notifications when application status changes"""
    if created:
        # Notify coordinator about new application
        coordinators = User.objects.filter(profile__user_type='coordinator')
        for coordinator in coordinators:
            Notification.objects.create(
                user=coordinator,
                notification_type='info',
                title='New Attachment Application',
                message=f"{instance.student.user_profile.user.get_full_name()} has submitted an application to {instance.organization.name}",
                link=f"/applications/{instance.id}/"
            )
    else:
        # Check if status changed
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            new_status = instance.status
            
            # Notify student
            Notification.objects.create(
                user=instance.student.user_profile.user,
                notification_type='success' if new_status == 'approved' else 'warning',
                title=f'Application Status Updated',
                message=f'Your application to {instance.organization.name} is now {instance.get_status_display()}',
                link=f"/applications/{instance.id}/"
            )
            
            # If approved, notify assigned supervisor
            if new_status == 'approved' and instance.assigned_supervisor:
                Notification.objects.create(
                    user=instance.assigned_supervisor.user_profile.user,
                    notification_type='info',
                    title='New Student Assigned',
                    message=f"You have been assigned to supervise {instance.student.user_profile.user.get_full_name()} at {instance.organization.name}",
                    link=f"/applications/{instance.id}/"
                )

@receiver(post_save, sender=LogBook)
def notify_supervisors_on_logbook(sender, instance, created, **kwargs):
    """Notify supervisors when new logbook entry is submitted"""
    if created:
        # Notify industry supervisor
        if instance.application.industry_supervisor_email:
            # In a real system, send email here
            pass
        
        # Notify university supervisor
        if instance.application.assigned_supervisor:
            Notification.objects.create(
                user=instance.application.assigned_supervisor.user_profile.user,
                notification_type='info',
                title='New Logbook Entry',
                message=f"Week {instance.week_number} logbook submitted by {instance.application.student.user_profile.user.get_full_name()}",
                link=f"/logbook/{instance.application.id}/"
            )

@receiver(pre_save, sender=Organization)
def update_organization_verification(sender, instance, **kwargs):
    """Update verification expiry if status changes to verified"""
    if instance.pk:  # Existing object
        old = Organization.objects.get(pk=instance.pk)
        if old.verification_status != 'verified' and instance.verification_status == 'verified':
            # Set expiry to 1 year from now
            instance.verification_expiry = timezone.now().date() + timedelta(days=365)
            instance.verified_at = timezone.now()