from django.urls import path
from . import views
app_name = 'freelancer'
urlpatterns = [
    # -----------------------------
    # Auth / Dashboard
    # -----------------------------
    path("signup/", views.freelancer_signup, name="freelancer_signup"),
    

    # -----------------------------
    # 1️⃣ Profile
    # -----------------------------
    path("profile/", views.freelancer_profile_detail, name="freelancer_profile_detail"),
    path("profile/edit/", views.update_profile, name="freelancer_profile_edit"),
    path("profile/create/", views.create_profile, name="freelancer_profile_create"),

    # -----------------------------
    # 2️⃣ Skills
    # -----------------------------
    path("skills/", views.manage_skills, name="freelancer_skills"),
    path("skills/add/", views.manage_skills, name="freelancer_add_skill"),

    # -----------------------------
    # 3️⃣ Certifications
    # -----------------------------
    path("certifications/", views.manage_certifications, name="freelancer_certifications"),
    path("certifications/add/", views.add_certification, name="freelancer_add_certification"),

    # -----------------------------
    # 4️⃣ Portfolio
    # -----------------------------
    path("portfolio/", views.portfolio_list, name="freelancer_portfolio"),
    path("portfolio/add/", views.add_portfolio_item, name="freelancer_add_portfolio"),

    # -----------------------------
    # 5️⃣ Projects & Proposals
    # -----------------------------
    path("projects/available/", views.available_projects, name="freelancer_available_projects"),
    path("projects/assigned/", views.assigned_projects, name="freelancer_assigned_projects"),
    path("projects/<int:project_id>/", views.project_detail, name="freelancer_project_detail"),

    # --- Proposals ---
    path("proposals/", views.freelancer_proposals, name="freelancer_proposals"),
    path("projects/<int:project_id>/submit-proposal/", views.submit_proposal, name="freelancer_submit_proposal"),

    # -----------------------------
    # 6️⃣ Milestones
    # -----------------------------
    path("projects/<int:project_id>/milestones/", views.milestone_list, name="freelancer_milestones"),
    path("milestones/<int:milestone_id>/update/", views.update_milestone, name="freelancer_update_milestone"),
    path("milestones/<int:milestone_id>/delete/", views.delete_milestone, name="freelancer_delete_milestone"),
    path("projects/<int:project_id>/milestones/create/", views.create_milestone, name="freelancer_create_milestone"),

    # -----------------------------
    # 7️⃣ Notifications
    # -----------------------------
    path("notifications/", views.freelancer_notifications, name="freelancer_notifications"),

    # -----------------------------
    # 8️⃣ Feedback / Earnings
    # -----------------------------
    path("feedback/", views.feedback_list, name="freelancer_feedback"),
    # path("earnings/", views.freelancer_earnings, name="freelancer_earnings"),
]
