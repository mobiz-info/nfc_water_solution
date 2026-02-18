from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers
from invoice_management.models import Invoice

class Command(BaseCommand):
    help = 'Add credit invoice type based on customer'

    def handle(self, *args, **kwargs):
        invoices = Invoice.objects.filter(is_deleted=False)
        
        for invoice in invoices:
            if invoice.customer.sales_type=="CREDIT":
                invoice.invoice_type="credit_invoice"
                invoice.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated into credit invoice'))