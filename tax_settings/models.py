from django.db import models
import uuid

# Create your models here.
class Tax(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=True, blank=True)
    percentage = models.IntegerField(default=0)  
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
   
    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)