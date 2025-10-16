from django.shortcuts import render ,redirect
from .forms import FreelancerProfileForm , FreelancerSignupForm
from django.contrib.auth import login
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

from .forms import (
    FreelancerProfileForm,
    ProposalForm,
    MilestoneForm,
    SkillForm,
    CertificationForm,
    PortfolioForm
)
from accounts.models import Notification
from projects.models import Project, ProjectProposal
from .models import FreelancerProfile, Skill, Certification, PortfolioItem
from accounts.supabase_helper import upload_to_supabase


# ----------------------------------------
# Helper
# ----------------------------------------
def role_required(role):
    """Custom role check for freelancers."""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role != role:
                messages.error(request, "Access denied.")
                return redirect('login')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator



def freelancer_signup(request):
    if request.method == 'POST':
        user_form = FreelancerSignupForm(request.POST)
        profile_form = FreelancerProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('freelancer_dashboard')  # ✅ corrected redirect
        else:
            print("❌ Form errors:", user_form.errors, profile_form.errors)
    else:
        user_form = FreelancerSignupForm()
        profile_form = FreelancerProfileForm()
    return render(request, 'freelancersignup.html', {'user_form': user_form, 'profile_form': profile_form})




# ----------------------------------------
# 1️⃣ Dashboard
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_dashboard(request):
    profile = request.user.freelancer_profile
    proposals = ProjectProposal.objects.filter(freelancer=profile)
    
    # Get assigned projects through ProjectAssignment
    assigned_projects = Project.objects.filter(assignment__freelancer=profile)
    completed_projects = assigned_projects.filter(status='COMPLETED')

    # Optional: Calculate earnings
    earnings = sum(profile.earnings.values_list('amount', flat=True))

    context = {
        'profile': profile,
        'proposals_count': proposals.count(),
        'pending_proposals': proposals.filter(status='PENDING').count(),
        'assigned_count': assigned_projects.count(),
        'completed_count': completed_projects.count(),
        'earnings': earnings,
        'notifications_count': request.user.notifications.filter(read=False).count(),
        'notifications': request.user.notifications.all().order_by('-created_at')[:5],
    }
    return render(request, 'Fdashboard.html', context)


# ----------------------------------------
# 2️⃣ Profile Management
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def create_profile(request):
    if hasattr(request.user, 'freelancer_profile'):
        return redirect('update_freelancer_profile')

    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user

            if 'profile_picture' in request.FILES:
                try:
                    img_url = upload_to_supabase(request.FILES['profile_picture'], folder='freelancers')
                    profile.profile_picture = img_url
                except Exception as e:
                    print("⚠️ Image upload failed:", e)

            profile.save()
            messages.success(request, "Profile created successfully.")
            return redirect('freelancer_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = FreelancerProfileForm()

    return render(request, 'freelancer/create_profile.html', {'form': form})


@login_required
@role_required('FREELANCER')
def update_profile(request):
    profile = request.user.freelancer_profile
    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            if 'profile_picture' in request.FILES:
                try:
                    img_url = upload_to_supabase(request.FILES['profile_picture'], folder='freelancers')
                    prof.profile_picture = img_url
                except Exception as e:
                    print("⚠️ Image upload failed:", e)
            prof.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('freelancer_profile_detail')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FreelancerProfileForm(instance=profile)
    return render(request, 'freelancer/update_profile.html', {'form': form, 'profile': profile})


@login_required
@role_required('FREELANCER')
def freelancer_profile_detail(request):
    profile = request.user.freelancer_profile
    return render(request, 'freelancer/profile_detail.html', {'profile': profile})


# ----------------------------------------
# 3️⃣ Browse Projects & Proposals
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def available_projects(request):
    profile = request.user.freelancer_profile

    # ✅ Projects that are not assigned and still in PLANNED status
    projects = Project.objects.filter(
        assigned_to_freelancers=False,
        status='PLANNED'
    )

    return render(request, 'available_projects.html', {
        'projects': projects,
        'profile': profile
    })



# ----------------------------------------
# 2️⃣ Project Detail + Existing Proposal
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    # Check if the freelancer already applied
    existing_proposal = ProjectProposal.objects.filter(
        project=project,
        freelancer=freelancer
    ).first()

    return render(request, 'project_detail.html', {
        'project': project,
        'proposal': existing_proposal
    })



# ----------------------------------------
# 3️⃣ Submit a Proposal
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    # Prevent duplicate proposals
    if ProjectProposal.objects.filter(project=project, freelancer=freelancer).exists():
        messages.info(request, "You already submitted a proposal for this project.")
        return redirect('freelancer_proposals')

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = freelancer
            proposal.status = 'PENDING'
            proposal.save()

            messages.success(request, "Proposal submitted successfully.")
            return redirect('freelancer_proposals')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProposalForm()

    return render(request, 'submit_proposal.html', {
        'form': form,
        'project': project
    })



# ----------------------------------------
# 4️⃣ View All My Proposals
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_proposals(request):
    proposals = ProjectProposal.objects.filter(
        freelancer=request.user.freelancer_profile
    ).select_related('project')
    
    return render(request, 'proposals_list.html', {
        'proposals': proposals
    })



# ----------------------------------------
# 5️⃣ Assigned Projects
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def assigned_projects(request):
    freelancer = request.user.freelancer_profile

    projects = Project.objects.filter(
        assigned_to_freelancers=True,
        proposals__freelancer=freelancer,
        proposals__status='ACCEPTED'
    ).distinct()

    return render(request, 'assigned_projects.html', {
        'projects': projects
    })

@login_required
@role_required('FREELANCER')
def project_milestones(request, project_id):
    project = get_object_or_404(Project, id=project_id, assigned_freelancer=request.user.freelancer_profile)
    milestones = ProjectMilestone.objects.filter(project=project)
    return render(request, 'freelancer/project_milestones.html', {'project': project, 'milestones': milestones})


@login_required
@role_required('FREELANCER')
def update_milestone(request, milestone_id):
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id, project__assigned_freelancer=request.user.freelancer_profile)
    if request.method == 'POST':
        form = MilestoneUpdateForm(request.POST, request.FILES, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('project_milestones', project_id=milestone.project.id)
    else:
        form = MilestoneUpdateForm(instance=milestone)
    return render(request, 'freelancer/update_milestone.html', {'form': form, 'milestone': milestone})


# ----------------------------------------
# 5️⃣ Skills & Certifications
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def manage_skills(request):
    profile = request.user.freelancer_profile
    skills = Skill.objects.filter(freelancer=profile)
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.freelancer = profile
            skill.save()
            messages.success(request, "Skill added successfully.")
            return redirect('manage_skills')
    else:
        form = SkillForm()
    return render(request, 'freelancer/manage_skills.html', {'skills': skills, 'form': form})


@login_required
@role_required('FREELANCER')
def add_certification(request):
    profile = request.user.freelancer_profile
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.freelancer = profile
            cert.save()
            messages.success(request, "Certification added successfully.")
            return redirect('manage_certifications')
    else:
        form = CertificationForm()
    return render(request, 'freelancer/add_certification.html', {'form': form})


@login_required
@role_required('FREELANCER')
def manage_certifications(request):
    profile = request.user.freelancer_profile
    certifications = Certification.objects.filter(freelancer=profile)
    return render(request, 'freelancer/manage_certifications.html', {'certifications': certifications})


# ----------------------------------------
# 6️⃣ Portfolio Management
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def portfolio_list(request):
    profile = request.user.freelancer_profile
    items = PortfolioItem.objects.filter(freelancer=profile)
    return render(request, 'freelancer/portfolio_list.html', {'items': items})


@login_required
@role_required('FREELANCER')
def add_portfolio_item(request):
    profile = request.user.freelancer_profile
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.freelancer = profile
            if 'file' in request.FILES:
                try:
                    file_url = upload_to_supabase(request.FILES['file'], folder='portfolios')
                    item.file = file_url
                except Exception as e:
                    print("File upload error:", e)
            item.save()
            messages.success(request, "Portfolio item added successfully.")
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()
    return render(request, 'freelancer/add_portfolio.html', {'form': form})


# ----------------------------------------
# 7️⃣ Notifications & Feedback
# ----------------------------------------
@login_required
@role_required('FREELANCER')
def freelancer_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'freelancer/notifications.html', {'notifications': notifications})


@login_required
@role_required('FREELANCER')
def feedback_list(request):
    feedbacks = Feedback.objects.filter(freelancer=request.user.freelancer_profile)
    return render(request, 'freelancer/feedback_list.html', {'feedbacks': feedbacks})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Milestone, FreelancerProfile
from projects.models import Project
from .forms import MilestoneForm
from accounts.models import Notification


# ------------------------------------------------
# LIST MILESTONES FOR A PROJECT
# ------------------------------------------------
@login_required
def milestone_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project, freelancer=request.user.freelancer_profile)
    return render(request, 'freelancer/milestone_list.html', {'project': project, 'milestones': milestones})


# ------------------------------------------------
# CREATE NEW MILESTONE
# ------------------------------------------------
@login_required
def create_milestone(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    freelancer = request.user.freelancer_profile

    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.freelancer = freelancer
            milestone.save()

            # Notify startup about new milestone
            Notification.objects.create(
                user=project.startup.user,
                title="New Milestone Created",
                message=f"{freelancer.full_name} added a new milestone '{milestone.title}' for project '{project.title}'."
            )

            messages.success(request, "Milestone created successfully.")
            return redirect('milestone_list', project_id=project.id)
    else:
        form = MilestoneForm()

    return render(request, 'freelancer/milestone_form.html', {'form': form, 'project': project, 'create': True})


# ------------------------------------------------
# UPDATE MILESTONE
# ------------------------------------------------
@login_required
def update_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id, freelancer=request.user.freelancer_profile)
    project = milestone.project

    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            updated = form.save(commit=False)

            # Auto update status
            if updated.progress == 100:
                updated.status = 'COMPLETED'

                # Notify startup
                Notification.objects.create(
                    user=project.startup.user,
                    title="Milestone Completed",
                    message=f"{milestone.freelancer.full_name} marked the milestone '{milestone.title}' as completed."
                )

            updated.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('milestone_list', project_id=project.id)
    else:
        form = MilestoneForm(instance=milestone)

    return render(request, 'freelancer/milestone_form.html', {
        'form': form,
        'project': project,
        'update': True,
        'milestone': milestone
    })


# ------------------------------------------------
# DELETE MILESTONE
# ------------------------------------------------
@login_required
def delete_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id, freelancer=request.user.freelancer_profile)
    project_id = milestone.project.id
    milestone.delete()
    messages.success(request, "Milestone deleted successfully.")
    return redirect('milestone_list', project_id=project_id)


