import datetime

from django.core.management.base import BaseCommand

from client_management.models import CustomerCouponItems, CustomerCouponStock, CustomerSupply
from invoice_management.models import Invoice

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        customer_coupon_items = CustomerCouponItems.objects.all()
        
        for item in customer_coupon_items:
            available_coupon_count = item.get_available_coupon_count()
            # CustomerCouponStock.objects.filter(customer=item.customer_coupon.customer,coupon_type_id=item.coupon.coupon_type).delete()
            
            if CustomerCouponStock.objects.filter(customer=item.customer_coupon.customer,coupon_type_id=item.coupon.coupon_type).exists():
                customer_stock = CustomerCouponStock.objects.get(customer=item.customer_coupon.customer,coupon_type_id=item.coupon.coupon_type)
            else:
                customer_stock = CustomerCouponStock.objects.create(customer=item.customer_coupon.customer,coupon_type_id=item.coupon.coupon_type,count=0)
                
            customer_stock.count += available_coupon_count
            customer_stock.save()
            
            self.stdout.write(self.style.WARNING(f'Successfully updated {item.customer_coupon.customer.customer_name} --- {available_coupon_count}  --- {item.coupon.book_num}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
