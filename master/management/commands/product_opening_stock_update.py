from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from product.models import NextDayStockRequest, Staff_IssueOrders
from van_management.models import VanProductStock

class Command(BaseCommand):
    help = 'Update or create opening counts for today based on yesterday\'s closing counts'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        total_stock = 0
        nextday_stock = 0
        
        yesterday_stocks = VanProductStock.objects.filter(created_date=yesterday)
        
        for yesterday_stock in yesterday_stocks:
            # Separate the lookup and creation logic
            total_stock = yesterday_stock.stock
            today_stock = VanProductStock.objects.filter(
                product=yesterday_stock.product,
                van=yesterday_stock.van,
                created_date=today
            ).first()

            if today_stock:
                today_stock.opening_count += yesterday_stock.closing_count
                today_stock.stock += total_stock
                today_stock.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated opening count for {today_stock.id}'))
            else:
                today_stock = VanProductStock.objects.create(
                    product=yesterday_stock.product,
                    van=yesterday_stock.van,
                    created_date=today,
                    opening_count=yesterday_stock.closing_count,
                    change_count=yesterday_stock.change_count,
                    damage_count=yesterday_stock.damage_count,
                    empty_can_count=yesterday_stock.empty_can_count,
                    return_count=yesterday_stock.return_count,
                    stock=total_stock
                )
        
            if (nextday_instances:=NextDayStockRequest.objects.filter(date=today,product=yesterday_stock.product,van=yesterday_stock.van)).exists():
                nextday_stock = int(nextday_instances.first().issued_quantity)
            
        self.stdout.write(self.style.SUCCESS('Stock update process completed.'))
