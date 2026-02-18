from django.core.management.base import BaseCommand
from django.db.models import Count
from invoice_management.models import Invoice

class Command(BaseCommand):
    help = 'Find invoices with duplicate invoice IDs'

    def handle(self, *args, **kwargs):
        # Find duplicate custom_ids
        duplicates = Invoice.objects.values('invoice_no') \
            .annotate(id_count=Count('id')) \
            .filter(id_count__gt=1)

        if duplicates.exists():
            self.stdout.write(self.style.WARNING('Duplicate invoice IDs found:'))
            
            for dup in duplicates:
                # Fetch customers with the duplicate custom_id
                duplicate_invoices = Invoice.objects.filter(invoice_no=dup['invoice_no'])
                
                self.stdout.write(f"invoice ID: {dup['invoice_no']}")
                
                for invoice in duplicate_invoices:
                    self.stdout.write(f"  - invoice ID: {invoice.invoice_no}, Name: {invoice.customer.customer_name}, Created Date: {invoice.created_date}")
        else:
            self.stdout.write(self.style.SUCCESS('No duplicate custom IDs found.'))
