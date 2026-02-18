from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum, F, DecimalField

from accounts.models import Customers
from invoice_management.models import Invoice
from client_management.models import CustomerOutstandingReport


class Command(BaseCommand):
    help = "Fix all customer outstanding reports by correcting invoices and recalculating pending amounts"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("============== FIX OUTSTANDING REPORT STARTED =============="))

        customers = Customers.objects.all()

        for customer in customers:
            self.stdout.write(f"\nCustomer: {customer.customer_name} (ID: {customer.pk})")

            # --------------------------------------------------------
            # 1️⃣ FIX NEGATIVE INVOICES BEFORE CALCULATING OUTSTANDING
            # --------------------------------------------------------
            invoices = Invoice.objects.filter(customer=customer, is_deleted=False)

            for inv in invoices:
                pending = inv.amout_total - inv.amout_recieved

                if pending < 0:
                    self.stdout.write(self.style.WARNING(
                        f"⚠ Invoice {inv.invoice_no} has negative pending ({pending}) → FIXING"
                    ))

                    # Fix invoice
                    inv.amout_recieved = inv.amout_total
                    inv.invoice_status = "paid"
                    inv.save()

            # --------------------------------------------------------
            # 2️⃣ NOW CALCULATE CORRECT PENDING
            # --------------------------------------------------------
            result = invoices.aggregate(
                pending=Sum(
                    F("amout_total") - F("amout_recieved"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )

            pending = result["pending"] or Decimal("0.00")

            # Prevent negative total
            if pending < 0:
                pending = Decimal("0.00")

            self.stdout.write(f"Correct Pending After Fix: {pending}")

            # --------------------------------------------------------
            # 3️⃣ UPDATE OUTSTANDING REPORT
            # --------------------------------------------------------
            report, created = CustomerOutstandingReport.objects.update_or_create(
                customer=customer,
                product_type="amount",
                defaults={"value": pending},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"➡ Created OutstandingReport = {pending}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"➡ Updated OutstandingReport → {report.value}"))

        self.stdout.write(self.style.WARNING("\n============== FIX OUTSTANDING REPORT COMPLETED =============="))
