from django.db import models
from accounts.models import CustomUser

class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="freelancer_profile")
    skills = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Freelancer"
