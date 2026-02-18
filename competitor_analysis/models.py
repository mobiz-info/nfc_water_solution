from django.db import models
import uuid
from django.utils import timezone


class Competitor(models.Model):
    competitor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class CompetitorAnalysis(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    created_date = models.DateTimeField(default=timezone.now)  # Set default to current date and time
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
