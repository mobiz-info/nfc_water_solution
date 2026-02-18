from django.core.management.base import BaseCommand
from django.db.models import Sum, F
from datetime import datetime, date

from accounts.models import Customers
from client_management.models import OutstandingAmount
from invoice_management.models import Invoice
from sales_management.models import CollectionPayment


class Command(BaseCommand):
    help = "Find route-wise outstanding difference between report calculations"

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, required=True, help="Date to compare (YYYY-MM-DD)")
        parser.add_argument("--route", type=str, required=True, help="Route name")

    def handle(self, *args, **options):
        try:
            # Parse arguments
            route_name = options["route"]
            date_str = options["date"]
            d = datetime.strptime(date_str, "%Y-%m-%d").date()

            self.stdout.write(self.style.MIGRATE_HEADING(f"\n🔍 Comparing Outstanding as of {d} for Route: {route_name}\n"))

            # --- Outstanding up to and including date
            oa_lte = OutstandingAmount.objects.filter(
                customer_outstanding__customer__routes__route_name=route_name,
                customer_outstanding__created_date__date__lte=d
            ).aggregate(total=Sum('amount'))['total'] or 0

            # --- Outstanding up to before date
            oa_lt = OutstandingAmount.objects.filter(
                customer_outstanding__customer__routes__route_name=route_name,
                customer_outstanding__created_date__date__lt=d
            ).aggregate(total=Sum('amount'))['total'] or 0

            # --- Collections up to before date
            coll_lt = CollectionPayment.objects.filter(
                customer__routes__route_name=route_name,
                created_date__date__lt=d
            ).aggregate(total=Sum('amount_received'))['total'] or 0

            # --- Collections on the date
            coll_eq = CollectionPayment.objects.filter(
                customer__routes__route_name=route_name,
                created_date__date=d
            ).aggregate(total=Sum('amount_received'))['total'] or 0

            # --- Credit invoices (if any)
            credit_total = Invoice.objects.filter(
                invoice_type="credit_invoice",
                customer__routes__route_name=route_name,
                created_date__date__lte=d
            ).aggregate(total=Sum('amout_total'))['total'] or 0

            # --- Recompute both logic paths
            # From customer_outstanding_list logic (<= date)
            outstanding_list_total = oa_lte - (coll_lt + coll_eq)

            # From daily route logic (< date + credit - collection)
            todays_opening = oa_lt - coll_lt
            daily_logic_total = todays_opening + credit_total - coll_eq

            diff = outstanding_list_total - daily_logic_total

            self.stdout.write(self.style.SUCCESS(f"✅ Outstanding (<= date): {oa_lte:,.2f}"))
            self.stdout.write(self.style.SUCCESS(f"✅ Outstanding (< date): {oa_lt:,.2f}"))
            self.stdout.write(self.style.SUCCESS(f"💰 Collections (< date): {coll_lt:,.2f}"))
            self.stdout.write(self.style.SUCCESS(f"💰 Collections (= date): {coll_eq:,.2f}"))
            self.stdout.write(self.style.SUCCESS(f"📄 Credit Invoices: {credit_total:,.2f}\n"))

            self.stdout.write(self.style.MIGRATE_HEADING(f"📊 Customer Outstanding List Total: {outstanding_list_total:,.2f}"))
            self.stdout.write(self.style.MIGRATE_HEADING(f"📊 Daily Route Logic Total: {daily_logic_total:,.2f}"))
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n🔸 Difference: {diff:,.2f}\n"))

            # --- Identify individual mismatches
            if abs(diff) > 0.01:
                self.stdout.write(self.style.WARNING("🔎 Scanning per-customer differences...\n"))
                customers = Customers.objects.filter(routes__route_name=route_name).distinct()
                for c in customers:
                    oa_lte_c = OutstandingAmount.objects.filter(
                        customer_outstanding__customer=c,
                        customer_outstanding__created_date__date__lte=d
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    coll_lte_c = CollectionPayment.objects.filter(
                        customer=c,
                        created_date__date__lte=d
                    ).aggregate(total=Sum('amount_received'))['total'] or 0

                    net_cust = oa_lte_c - coll_lte_c

                    oa_lt_c = OutstandingAmount.objects.filter(
                        customer_outstanding__customer=c,
                        customer_outstanding__created_date__date__lt=d
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    coll_lt_c = CollectionPayment.objects.filter(
                        customer=c,
                        created_date__date__lt=d
                    ).aggregate(total=Sum('amount_received'))['total'] or 0

                    coll_eq_c = CollectionPayment.objects.filter(
                        customer=c,
                        created_date__date=d
                    ).aggregate(total=Sum('amount_received'))['total'] or 0

                    credit_c = Invoice.objects.filter(
                        invoice_type="credit_invoice",
                        customer=c,
                        created_date__date__lte=d
                    ).aggregate(total=Sum('amout_recieved'))['total'] or 0

                    todays_opening_c = oa_lt_c - coll_lt_c
                    daily_logic_c = todays_opening_c + credit_c - coll_eq_c

                    diff_c = net_cust - daily_logic_c

                    if abs(diff_c) > 0.009:
                        self.stdout.write(
                            f"{c.customer_name:<30}  Diff: {diff_c:>10.2f}  "
                            f"OutstandingList: {net_cust:>10.2f}  DailyLogic: {daily_logic_c:>10.2f}"
                        )

            self.stdout.write(self.style.SUCCESS("\n✅ Done."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
