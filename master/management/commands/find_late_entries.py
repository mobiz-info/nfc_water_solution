from django.core.management.base import BaseCommand
from django.db.models import Sum
from datetime import datetime
from client_management.models import CustomerOutstanding, Customers
from master.models import RouteMaster  # adjust if in another app


class Command(BaseCommand):
    help = "Find route-wise customers whose outstanding differs between two dates."

    def add_arguments(self, parser):
        parser.add_argument('--date1', type=str, required=True, help='First date (YYYY-MM-DD)')
        parser.add_argument('--date2', type=str, required=True, help='Second date (YYYY-MM-DD)')
        parser.add_argument('--min_diff', type=float, default=0.01, help='Minimum difference to show (e.g. 10 for ₹10)')
        parser.add_argument('--route', type=str, default=None, help='Specific route name to check (optional)')

    def handle(self, *args, **options):
        date1 = datetime.strptime(options['date1'], "%Y-%m-%d").date()
        date2 = datetime.strptime(options['date2'], "%Y-%m-%d").date()
        min_diff = options['min_diff']
        route_name = options['route']

        self.stdout.write(self.style.WARNING(f"\n🔍 Comparing outstanding between {date1} and {date2}\n"))

        routes = RouteMaster.objects.all().order_by("route_name")
        if route_name:
            routes = routes.filter(route_name__iexact=route_name)

        if not routes.exists():
            self.stdout.write(self.style.ERROR("❌ No matching routes found.\n"))
            return

        for route in routes:
            self.stdout.write(self.style.HTTP_INFO(f"\n🚛 Route: {route.route_name}"))
            self.stdout.write("-" * 80)

            # Get customer IDs for this route
            customer_ids = Customers.objects.filter(routes=route).values_list("customer_id", flat=True)

            if not customer_ids:
                self.stdout.write("⚠️ No customers in this route.\n")
                continue

            # Outstanding up to each date
            outstanding_date1 = (
                CustomerOutstanding.objects
                .filter(created_date__date__lte=date1, customer_id__in=customer_ids)
                .values('customer_id')
                .annotate(total_amount=Sum('outstandingamount__amount'))
            )

            outstanding_date2 = (
                CustomerOutstanding.objects
                .filter(created_date__date__lte=date2, customer_id__in=customer_ids)
                .values('customer_id')
                .annotate(total_amount=Sum('outstandingamount__amount'))
            )

            # Map results for diff calculation
            outstanding_map_1 = {o['customer_id']: o['total_amount'] or 0 for o in outstanding_date1}
            outstanding_map_2 = {o['customer_id']: o['total_amount'] or 0 for o in outstanding_date2}

            all_customer_ids = set(outstanding_map_1.keys()) | set(outstanding_map_2.keys())
            diff_list = []

            for cid in all_customer_ids:
                amt1 = outstanding_map_1.get(cid, 0)
                amt2 = outstanding_map_2.get(cid, 0)
                diff = amt2 - amt1
                if abs(diff) >= min_diff:
                    diff_list.append((cid, amt1, amt2, diff))

            if not diff_list:
                self.stdout.write("✅ No outstanding differences found for this route.\n")
                continue

            self.stdout.write(self.style.NOTICE(f"⚠️ Found {len(diff_list)} customers with diff ≥ {min_diff}\n"))

            for cid, amt1, amt2, diff in diff_list:
                customer = Customers.objects.filter(pk=cid).first()
                name = customer.customer_name if customer else f"ID {cid}"
                self.stdout.write(f"  • {name:40s} | {amt1:10.2f} → {amt2:10.2f} | Δ {diff:+.2f}")

        self.stdout.write(self.style.SUCCESS("\n✅ Route-wise outstanding difference check complete!"))
