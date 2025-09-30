from django import forms
from accounts.models import CustomUser
from .models import StartupProfile ,Employee
from django.contrib.auth.forms import UserCreationForm
from projects.models import Project
from funding.models import FundingRound
from mentors.models import MentorshipSession

class StartupSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STARTUP'
        if commit:
            user.save()
        return user

class StartupProfileForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    class Meta:
        model = StartupProfile
        fields = ['startup_name', 'description', 'website', 'founded_date', 'industry', 'logo']
        
        

class ProjectForm(forms.ModelForm):
    requirements_file_upload = forms.FileField(required=False)
    employees_assigned = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(),  # will set queryset dynamically
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'start_date', 'end_date', 'status',
                  'assigned_to_freelancers', 'employees_assigned', 'requirements_file_upload')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        if startup:
            # Only show employees of this startup
            self.fields['employees_assigned'].queryset = startup.employees.all()
            
            

class EmployeeForm(forms.ModelForm):
    date_of_joining = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Employee
        fields = [
            'name', 'role', 'email', 'phone_number', 'profile_picture',
            'linkedin_profile', 'github_profile', 'skills', 'date_of_joining', 'is_active'
        ]
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python, Django, React'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g., Developer, Designer'}),
        }
        labels = {
            'is_active': 'Currently Active',
            'profile_picture': 'Upload Profile Picture',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Customize labels or help texts
        self.fields['is_active'].label = "Currently Active"
        self.fields['profile_picture'].label = "Upload Profile Picture"
        
        

# -----------------------------
# FUNDING FORM
# -----------------------------
class FundingForm(forms.ModelForm):
    class Meta:
        model = FundingRound
        fields = ['investor', 'round_name', 'amount', 'status']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }


# -----------------------------
# MENTORSHIP FORM
# -----------------------------
class MentorshipForm(forms.ModelForm):
    class Meta:
        model = MentorshipSession
        fields = ['mentor', 'topic', 'status', 'session_date']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
        }