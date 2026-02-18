from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from van_management.models import VanCouponStock

class Command(BaseCommand):
    help = 'Update or create opening counts for today based on yesterday\'s closing counts for VanCouponStock'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Fetch all VanCouponStock entries for yesterday
        yesterday_stocks = VanCouponStock.objects.filter(created_date=yesterday,closing_count__gt=0)
        
        for yesterday_stock in yesterday_stocks:
            # Get or create today's stock entry
            today_stock, created = VanCouponStock.objects.get_or_create(
                coupon=yesterday_stock.coupon,
                van=yesterday_stock.van,
                created_date=today,  # Ensure created_date is set to today
                defaults={
                    'opening_count': yesterday_stock.closing_count,
                    'stock': yesterday_stock.stock,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created new coupon stock entry for {today_stock.id}'))
            else:
                today_stock.opening_count = yesterday_stock.closing_count
                today_stock.save()
                self.stdout.write(self.style.SUCCESS(f'Updated opening count for {today_stock.id}'))
