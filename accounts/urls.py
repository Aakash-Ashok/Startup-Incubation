from django.urls import path
from . import views
from freelancer.views import freelancer_dashboard
urlpatterns = [
    path("dashboard/", freelancer_dashboard, name="freelancer_dashboard"),
    path('logout/', views.logout_view, name='logout'),
]
