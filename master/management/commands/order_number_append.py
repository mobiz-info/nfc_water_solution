from django.core.management.base import BaseCommand
from django.utils import timezone
from product.models import Staff_Orders

class Command(BaseCommand):
    help = 'Add Order ID for each orders based on created date'

    def handle(self, *args, **kwargs):
        orders = Staff_Orders.objects.order_by('created_date')

        order_number_counter = 1

        for order in orders:
            order_number = f"{order_number_counter}"
            order.order_number = order_number
            order.save()

            order_number_counter += 1

        self.stdout.write(self.style.SUCCESS('Order IDs added successfully for all Orders.'))


