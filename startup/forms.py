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
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'requirements_file',
            'start_date', 'end_date', 'status',
            'assigned_to_freelancers', 'employees_assigned'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project details...'}),
            'requirements_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'employees_assigned': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        if startup:
            self.fields['employees_assigned'].queryset = Employee.objects.filter(startup=startup)
        else:
            self.fields['employees_assigned'].queryset = Employee.objects.none()


            

# forms.py
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'role', 'email', 'phone_number', 'profile_picture',
            'linkedin_profile', 'github_profile', 'skills', 'date_of_joining', 'is_active'
        ]

        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python, Django, React'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g., Developer, Designer'}),
            'date_of_joining': forms.DateInput(
                attrs={'type': 'date'}  # ✅ This ensures the HTML5 date picker appears
            ),
        }


        
        

# -----------------------------
# FUNDING FORM
# -----------------------------
class FundingForm(forms.ModelForm):
    all_investors = forms.BooleanField(
        required=False,
        label="Send to all investors",
        help_text="Check to notify all investors instead of a specific one."
    )

    class Meta:
        model = FundingRound
        fields = ['round_name', 'amount', 'investor', 'all_investors']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        investor = cleaned_data.get('investor')
        all_investors = cleaned_data.get('all_investors')

        if not all_investors and not investor:
            raise forms.ValidationError("Select either a specific investor or 'all investors'.")
        if all_investors and investor:
            raise forms.ValidationError("Cannot select both a specific investor and 'all investors'.")
        return cleaned_data


# -----------------------------
# MENTORSHIP FORM
# -----------------------------
class MentorshipSessionForm(forms.ModelForm):
    class Meta:
        model = MentorshipSession
        fields = ['mentor', 'topic', 'session_date', 'notes']
        widgets = {
            'session_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add objectives or notes for mentor'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop custom argument to disable all fields if needed
        disable_all = kwargs.pop('disable_all', False)
        super().__init__(*args, **kwargs)
        if disable_all:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

