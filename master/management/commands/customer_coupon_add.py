from django.db.models import Sum
from django.utils import timezone
from django.core.management.base import BaseCommand
from accounts.models import Customers
from client_management.models import CustomerCouponStock

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        customers = Customers.objects.order_by('created_date')

        for customer in customers:
            coupons_count = 0
            
            if (customer_coupon_stock:=CustomerCouponStock.objects.filter(customer=customer)).exists() :
                coupons_count = customer_coupon_stock.aggregate(total_count=Sum('count'))['total_count']
            
            customer.coupon_count = coupons_count
            customer.save()

        self.stdout.write(self.style.SUCCESS('Custom coupon count added successfully for all customers.'))


