from django.db import models
from accounts.models import CustomUser
from startup.models import StartupProfile

class InvestorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="investor_profile")
    company = models.CharField(max_length=200, blank=True, null=True)
    investment_focus = models.CharField(max_length=200, blank=True, null=True)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - Investor"

class FundingRound(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="funding_rounds")
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="fundings")
    round_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ], default='REQUESTED')

    def __str__(self):
        return f"{self.startup.startup_name} - {self.round_name}"
