from django.db import models

class DashboardAnalytics(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total_startups = models.PositiveIntegerField(default=0)
    total_freelancers = models.PositiveIntegerField(default=0)
    total_projects = models.PositiveIntegerField(default=0)
    total_funding = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return f"Analytics Snapshot {self.created_at}"
