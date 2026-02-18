from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.timezone import make_aware
from datetime import datetime

from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount


class Command(BaseCommand):
    help = "Update existing OutstandingAmount records to match Invoice amounts (NO CREATE, NO DELETE)."

    def handle(self, *args, **kwargs):

        start_date = make_aware(datetime(2025, 9, 1))
        end_date = make_aware(datetime(2025, 11, 30, 23, 59, 59))

        # route = "S-01"

        invoices = Invoice.objects.filter(
            created_date__range=(start_date, end_date),
            # customer__routes__route_name=route,
            is_deleted=False
        ).exclude(invoice_no__isnull=True).exclude(invoice_no__exact="")

        updated_count = 0

        for inv in invoices:

            invoice_amount = inv.amout_total or 0
            invoice_no = inv.invoice_no
            customer = inv.customer

            # Fetch existing CustomerOutstanding (NO CREATE)
            outstanding = CustomerOutstanding.objects.filter(
                customer=customer,
                invoice_no=invoice_no,
                product_type="amount"
            ).first()

            if not outstanding:
                continue  # skip if header not exist

            # Fetch existing OutstandingAmount rows
            outstanding_row = OutstandingAmount.objects.filter(
                customer_outstanding=outstanding
            ).first()

            if not outstanding_row:
                continue  # skip if no amount row exists

            # Compare and update
            if float(outstanding_row.amount) != float(invoice_amount):

                old_amount = outstanding_row.amount
                outstanding_row.amount = invoice_amount
                outstanding_row.save()

                updated_count += 1

                self.stdout.write(
                    f"Updated {invoice_no}: {old_amount} → {invoice_amount}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nFinished! Updated {updated_count} outstanding amount records for route all."
        ))
