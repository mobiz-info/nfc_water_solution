from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        customers = Customers.objects.filter(is_guest=False, visit_schedule="Monday ")
        
        # Update visit_schedule for each customer
        for customer in customers:
            # Update the visit_schedule field with the provided format
            customer.visit_schedule = {
                "Friday": [""],
                "Monday": [""],
                "Sunday": [""],
                "Tuesday": [""],
                "Saturday": [""],
                "Thursday": [""],
                "Wednesday": [""]
            }
            # Save the updated customer
            customer.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated visit schedule for customers with visit_schedule="Saturday"'))