from django.db import models
from startup.models import StartupProfile
from freelancer.models import FreelancerProfile
from startup.models import Employee

class Project(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=200)
    description = models.TextField()
    requirements_file = models.FileField(upload_to='project_requirements/', blank=True, null=True)  # Local file storage
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('PLANNED', 'Planned'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed')
    ], default='PLANNED')
    
    assigned_to_freelancers = models.BooleanField(default=False)
    employees_assigned = models.ManyToManyField(Employee, blank=True, related_name='projects')

    def __str__(self):
        return f"{self.name} ({self.startup.startup_name})"

class ProjectProposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="proposals")
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name="proposals")
    proposal_text = models.TextField()
    file = models.FileField(upload_to='proposal_attachments/')
    expected_timeline = models.CharField(max_length=100, blank=True, null=True)
    expected_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ], default='PENDING')
    rejection_note = models.TextField(blank=True, null=True)  # NEW: store rejection reason
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.freelancer.user.username} Proposal"

class ProjectAssignment(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="assignment")
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, null=True, blank=True)
    employee_name = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.freelancer:
            return f"{self.project.name} -> {self.freelancer.user.username}"
        return f"{self.project.name} -> {self.employee_name}"
    
    

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to_freelancer = models.ForeignKey(FreelancerProfile, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to_employee = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING','Pending'),
        ('ONGOING','Ongoing'),
        ('COMPLETED','Completed')
    ], default='PENDING')
    deadline = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"
