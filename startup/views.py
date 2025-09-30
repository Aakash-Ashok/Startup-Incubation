from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import StartupSignupForm, StartupProfileForm, ProjectForm, EmployeeForm, FundingForm, MentorshipForm
from accounts.supabase_helper import upload_to_supabase
from projects.models import Project, ProjectProposal ,ProjectAssignment
from funding.models import FundingRound
from .models import Employee
from mentors.models import *
from accounts.models import Notification

# -----------------------------
# 1️⃣ Auth / Signup
# -----------------------------
def startup_signup(request):
    if request.method == 'POST':
        user_form = StartupSignupForm(request.POST)
        profile_form = StartupProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'STARTUP'
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            logo_file = request.FILES.get('logo')
            if logo_file:
                logo_url = upload_to_supabase(logo_file, folder='startups')
                if logo_url:
                    profile.logo = logo_url
            profile.save()
            login(request, user)
            return redirect('startup_dashboard')
    else:
        user_form = StartupSignupForm()
        profile_form = StartupProfileForm()
    return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})

# -----------------------------
# 2️⃣ Dashboard
# -----------------------------
@login_required
def startup_dashboard(request):
    profile = request.user.startup_profile
    projects = Project.objects.filter(startup=profile)
    projects_count = projects.count()
    projects_in_progress = projects.filter(status='ONGOING').count()
    projects_completed = projects.filter(status='COMPLETED').count()
    projects_open = projects.filter(status='PLANNED').count()
    employees_count = profile.employees.count()
    proposals = ProjectProposal.objects.filter(project__startup=profile)
    proposals_count = proposals.count()
    proposals_approved = proposals.filter(status='APPROVED').count()
    proposals_rejected = proposals.filter(status='REJECTED').count()
    funding_qs = FundingRound.objects.filter(startup=profile)
    funding_count = funding_qs.count()
    funding_approved = funding_qs.filter(status='APPROVED').count()
    funding_rejected = funding_qs.filter(status='REJECTED').count()
    mentorship_qs = MentorshipSession.objects.filter(startup=profile)
    mentorship_count = mentorship_qs.filter(status='SCHEDULED').count()
    mentorship_completed = mentorship_qs.filter(status='COMPLETED').count()

    context = {
        'profile': profile,
        'projects_count': projects_count,
        'projects_open': projects_open,
        'projects_in_progress': projects_in_progress,
        'projects_completed': projects_completed,
        'employees_count': employees_count,
        'proposals_count': proposals_count,
        'proposals_approved': proposals_approved,
        'proposals_rejected': proposals_rejected,
        'funding_count': funding_count,
        'funding_approved': funding_approved,
        'funding_rejected': funding_rejected,
        'mentorship_count': mentorship_count,
        'mentorship_completed': mentorship_completed,
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile_detail(request):
    profile = request.user.startup_profile
    return render(request, 'startup/profile_detail.html', {'profile': profile})


# -----------------------------
# 3️⃣ Project CRUD
# -----------------------------
@login_required
def create_project(request):
    profile = request.user.startup_profile
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.startup = profile
            req_file = request.FILES.get('requirements_file')
            if req_file:
                req_url = upload_to_supabase(req_file, folder='project_requirements')
                if req_url:
                    project.requirements_file = req_url
            project.save()
            form.save_m2m()
            return redirect('startup_projects')
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form, 'profile': profile})

@login_required
def startup_projects(request):
    profile = request.user.startup_profile
    projects = Project.objects.filter(startup=profile)
    context = {
        'profile': profile,
        'projects': projects,
        'projects_count': projects.count(),
        'projects_in_progress': projects.filter(status='IN_PROGRESS').count(),
        'projects_completed': projects.filter(status='COMPLETED').count(),
        'notifications_count': request.user.notifications.filter(read=False).count(),
        'notifications': request.user.notifications.all().order_by('-created_at')[:5],
    }
    return render(request, 'projects_list.html', context)

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project, startup=request.user.startup_profile)
        if form.is_valid():
            project = form.save(commit=False)
            req_file = request.FILES.get('requirements_file_upload')
            if req_file:
                project.requirements_file = upload_to_supabase(req_file, folder='project_requirements')
            project.save()
            form.save_m2m()
            return redirect('startup_projects')
    else:
        form = ProjectForm(instance=project, startup=request.user.startup_profile)
    return render(request, 'startup/create_project.html', {'form': form, 'update': True})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    proposals = project.proposals.all()
    assigned_employees = project.employees_assigned.all()
    context = {
        'project': project,
        'proposals': proposals,
        'assigned_employees': assigned_employees,
    }
    return render(request, 'project_detail.html', context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        project.delete()
        return redirect('startup_projects')
    return render(request, 'startup/delete_project_confirm.html', {'project': project})

# -----------------------------
# 4️⃣ Project Proposals Workflow
# -----------------------------
@login_required
def project_proposals(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    proposals = project.proposals.all()
    return render(request, 'startup/project_proposals.html', {'project': project, 'proposals': proposals})

@login_required
def approve_proposal(request, proposal_id):
    proposal = get_object_or_404(ProjectProposal, id=proposal_id)
    proposal.status = 'APPROVED'
    proposal.save()

    project = proposal.project
    project.assigned_freelancer = proposal.freelancer
    project.status = 'ASSIGNED'
    project.save()

    # Notification to freelancer
    Notification.objects.create(
        user=proposal.freelancer.user,
        title="Project Proposal Approved",
        message=f"Your proposal for project '{project.name}' has been approved."
    )
    return redirect('project_proposals', project_id=project.id)

@login_required
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(ProjectProposal, id=proposal_id)
    proposal.status = 'REJECTED'
    proposal.save()

    # Notification to freelancer
    Notification.objects.create(
        user=proposal.freelancer.user,
        title="Project Proposal Rejected",
        message=f"Your proposal for project '{proposal.project.name}' has been rejected."
    )
    return redirect('project_proposals', project_id=proposal.project.id)

# -----------------------------
# 5️⃣ Employees Management
# -----------------------------
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)  # <-- include request.FILES
        if form.is_valid():
            employee = form.save(commit=False)
            employee.startup = request.user.startup_profile

            # Handle profile picture upload to Supabase
            profile_file = request.FILES.get('profile_picture')
            if profile_file:
                from accounts.supabase_helper import upload_to_supabase
                profile_url = upload_to_supabase(profile_file, folder='employee_profiles')
                if profile_url:
                    employee.profile_picture = profile_url

            employee.save()
            return redirect('startup_employees')
    else:
        form = EmployeeForm()
    return render(request, 'add_employee.html', {
        'form': form,
        'profile': request.user.startup_profile,
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY
    })


@login_required
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)  # <-- include request.FILES
        if form.is_valid():
            employee = form.save(commit=False)
            profile_file = request.FILES.get('profile_picture')
            if profile_file:
                from accounts.supabase_helper import upload_to_supabase
                profile_url = upload_to_supabase(profile_file, folder='employee_profiles')
                if profile_url:
                    employee.profile_picture = profile_url
            employee.save()
            form.save_m2m()
            return redirect('startup_employees')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'startup/add_employee.html', {'form': form, 'update': True})


@login_required
def startup_employees(request):
    # Get the startup profile for the logged-in user
    profile = request.user.startup_profile

    # Get all employees related to this startup
    employees = profile.employees.all()

    # Pass both profile and employees to the template
    context = {
        'profile': profile,
        'employees': employees,
    }
    return render(request, 'employee_list.html', context)

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    return render(request, 'employee_detail.html', {'employee': employee})


@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        employee.delete()
        return redirect('startup_employees')
    return render(request, 'delete_employee_confirm.html', {'employee': employee})

# -----------------------------
# 6️⃣ Notifications
# -----------------------------
@login_required
def notifications_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'startup/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('notifications_list')

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notification.read:
        notification.read = True
        notification.save()
    return render(request, 'startup/notification_detail.html', {'notification': notification})



# -----------------------------
# 7️⃣ Funding
# -----------------------------
@login_required
def funding_list(request):
    funding_rounds = FundingRound.objects.filter(startup=request.user.startup_profile)
    return render(request, 'startup/funding_list.html', {'funding_rounds': funding_rounds})

@login_required
def create_funding(request):
    if request.method == 'POST':
        form = FundingForm(request.POST)
        if form.is_valid():
            funding = form.save(commit=False)
            funding.startup = request.user.startup_profile
            funding.save()
            Notification.objects.create(
                user=funding.investor.user,
                title="Funding Round Created",
                message=f"{funding.startup.startup_name} created a funding round: {funding.round_name} for ${funding.amount}"
            )
            return redirect('funding_list')
    else:
        form = FundingForm()
    return render(request, 'startup/create_funding.html', {'form': form})

@login_required
def update_funding(request, funding_id):
    funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = FundingForm(request.POST, instance=funding)
        if form.is_valid():
            form.save()
            return redirect('funding_list')
    else:
        form = FundingForm(instance=funding)
    return render(request, 'startup/create_funding.html', {'form': form, 'update': True})

@login_required
def funding_detail(request, funding_id):
    funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)
    return render(request, 'startup/funding_detail.html', {'funding': funding})


@login_required
def delete_funding(request, funding_id):
    funding = get_object_or_404(FundingRound, id=funding_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        funding.delete()
        return redirect('funding_list')
    return render(request, 'startup/delete_funding_confirm.html', {'funding': funding})

# -----------------------------
# 8️⃣ Mentorship
# -----------------------------
@login_required
def mentorship_list(request):
    sessions = MentorshipSession.objects.filter(startup=request.user.startup_profile)
    return render(request, 'startup/mentorship_list.html', {'sessions': sessions})

@login_required
def create_mentorship(request):
    if request.method == 'POST':
        form = MentorshipForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.startup = request.user.startup_profile
            session.save()
            Notification.objects.create(
                user=session.mentor.user,
                title="Mentorship Scheduled",
                message=f"You have a mentorship session with {session.startup.startup_name} on {session.date}"
            )
            return redirect('mentorship_list')
    else:
        form = MentorshipForm()
    return render(request, 'startup/create_mentorship.html', {'form': form})

@login_required
def update_mentorship(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        form = MentorshipForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect('mentorship_list')
    else:
        form = MentorshipForm(instance=session)
    return render(request, 'startup/create_mentorship.html', {'form': form, 'update': True})

@login_required
def mentorship_detail(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)
    return render(request, 'startup/mentorship_detail.html', {'session': session})


@login_required
def delete_mentorship(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        session.delete()
        return redirect('mentorship_list')
    return render(request, 'startup/delete_mentorship_confirm.html', {'session': session})

# -----------------------------
# 9️⃣ Assign Employees (Internal)
# -----------------------------
@login_required
def assign_employee_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, startup=request.user.startup_profile)
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employees')
        project.employees_assigned.set(employee_ids)
        project.save()
        # Send notifications only to freelancers
        freelancers = project.employees_assigned.filter(role='FREELANCER')
        for freelancer in freelancers:
            Notification.objects.create(
                user=freelancer.user,
                title="Project Assigned",
                message=f"You have been assigned to project: {project.name}"
            )
        return redirect('startup_projects')
    employees = request.user.startup_profile.employees.all()
    return render(request, 'startup/assign_employee.html', {'project': project, 'employees': employees})


@login_required
def project_to_frelancer_list(request):
    project = ProjectAssignment.objects.filter(startup=request.user.startup_profile)
    return render(request, 'freelancerpro_list.html', {'project': project})
