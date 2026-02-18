import datetime
import random
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from accounts.models import CustomUser, Customers
from client_management.models import CustomerCoupon, CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyCoupon, OutstandingAmount
from invoice_management.models import Invoice, InvoiceItems
from master.models import RouteMaster
from product.models import ProdutItemMaster
from sales_management.models import CollectionItems, CollectionPayment

class Command(BaseCommand):
    help = "Deletes invoices not linked to supply, coupon, or outstanding for a given date (YYYY-MM-DD)"

    def add_arguments(self, parser):
        parser.add_argument('date', type=str, help='Target date in YYYY-MM-DD format')

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        date_str = options['date']
        dry_run = options['dry_run']

        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError("Invalid date format. Please use YYYY-MM-DD.")

        self.stdout.write(self.style.NOTICE(f"🔍 Checking invoices for {target_date}..."))

        # Step 1: All invoices of that date
        invoices = Invoice.objects.filter(created_date__date=target_date)

        if not invoices.exists():
            self.stdout.write(self.style.WARNING("No invoices found for this date."))
            return

        # Step 2: Collect invoice numbers used in related models
        supply_invoices = CustomerSupply.objects.filter(created_date__date=target_date).values_list('invoice_no', flat=True)
        coupon_invoices = CustomerCoupon.objects.filter(created_date__date=target_date).values_list('invoice_no', flat=True)
        outstanding_invoices = CustomerOutstanding.objects.filter(created_date__date=target_date).values_list('invoice_no', flat=True)

        used_invoices = set(supply_invoices) | set(coupon_invoices) | set(outstanding_invoices)

        # Step 3: Filter unlinked invoices
        unlinked_invoices = invoices.exclude(invoice_no__in=used_invoices,amout_total__lt=0,is_deleted=False)

        if not unlinked_invoices.exists():
            self.stdout.write(self.style.SUCCESS("✅ No unlinked invoices found. Nothing to delete."))
            return

        unlinked_nos = list(unlinked_invoices.values_list('invoice_no', flat=True))

        self.stdout.write(self.style.WARNING(f"🧾 Found {len(unlinked_nos)} unlinked invoice(s):"))
        for inv_no in unlinked_nos:
            self.stdout.write(f" - {inv_no}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("Dry run mode: no invoices deleted."))
            return

        # Step 4: Confirm and delete
        count, _ = unlinked_invoices.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} unlinked invoice(s) for {target_date}."))