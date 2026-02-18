import datetime
import random

from django.db.models import Q, Sum
from django.core.management.base import BaseCommand

from sales_management.models import CollectionItems, CollectionPayment, Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        collections = CollectionPayment.objects.all()
        for collection in collections:
            total_received = CollectionItems.objects.filter(collection_payment=collection).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
            collection.amount_received=total_received
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {collection.pk}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
