from django.urls import path
from . import views

urlpatterns = [
    
    path("signup/",views.freelancer_signup,name="freelancer_signup"),
    path("dashboard/",views.freelancer_dashboard,name="freelancer_dashboard"),
    # -----------------------------
    # 1️⃣ Freelancer Profile
    # -----------------------------
    path('profile/', views.freelancer_profile_detail, name='freelancer_profile_detail'),
    path('profile/edit/', views.update_profile, name='freelancer_profile_edit'),
    path('profile/create/', views.create_profile, name='create_freelancer_profile'),

    # -----------------------------
    # 2️⃣ Skills
    # -----------------------------
    path('skills/', views.manage_skills, name='manage_skills'),
    path('skills/add/', views.manage_skills, name='add_skill'),  # uses same view
    # Editing/deleting individual skills can be added if needed
    # path('skills/<int:skill_id>/edit/', views.edit_skill, name='edit_skill'),
    # path('skills/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),

    # -----------------------------
    # 3️⃣ Certifications
    # -----------------------------
    path('certifications/', views.manage_certifications, name='manage_certifications'),
    path('certifications/add/', views.add_certification, name='add_certification'),

    # -----------------------------
    # 4️⃣ Portfolio
    # -----------------------------
    path('portfolio/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/add/', views.add_portfolio_item, name='add_portfolio'),

    # -----------------------------
    # 5️⃣ Proposals
    # -----------------------------
    path('proposals/', views.freelancer_proposals, name='freelancer_proposals'),
    path('proposals/<int:project_id>/submit/', views.submit_proposal, name='submit_proposal'),

    # -----------------------------
    # 6️⃣ Assigned Projects & Milestones
    # -----------------------------
    path('projects/assigned/', views.assigned_projects, name='assigned_projects'),
    path('projects/<int:project_id>/', views.project_detail, name='freelancer_project_detail'),
    path('projects/<int:project_id>/milestones/', views.milestone_list, name='milestone_list'),
    path('milestones/<int:milestone_id>/update/', views.update_milestone, name='update_milestone'),
    path('milestones/<int:milestone_id>/delete/', views.delete_milestone, name='delete_milestone'),
    path('projects/<int:project_id>/milestones/create/', views.create_milestone, name='create_milestone'),

    # -----------------------------
    # 7️⃣ Notifications
    # -----------------------------
    path('notifications/', views.freelancer_notifications, name='freelancer_notifications'),
    # Optional detail/read views
    # path('notifications/<int:notification_id>/', views.notification_detail, name='freelancer_notification_detail'),
    # path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='freelancer_mark_notification_read'),

    # -----------------------------
    # 8️⃣ Feedback & Earnings
    # -----------------------------
    path('feedback/', views.feedback_list, name='freelancer_feedback_list'),
    # Earnings view if you have implemented it
    # path('earnings/', views.freelancer_earnings, name='freelancer_earnings'),
]
