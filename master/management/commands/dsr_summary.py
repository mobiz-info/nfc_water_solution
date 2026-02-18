from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round
from datetime import datetime

from accounts.models import Customers
from client_management.models import CustodyCustom, CustomerSupply, OutstandingAmount
from customer_care.models import DiffBottlesModel
from sales_management.models import CollectionPayment
from van_management.models import Expense, Van, VanProductStock, Van_Routes, VanSaleDamage


class Command(BaseCommand):
    help = "Generate Daily Sales Report (DSR) Summary for a given date and route."

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", required=True)
        parser.add_argument("--route_name", type=str, help="Route name", required=True)

    def handle(self, *args, **options):
        date_str = options["date"]
        route_name = options["route_name"]

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.stdout.write(f"Generating DSR summary for {route_name} on {date}...")

        # Initialize counters and totals
        new_customers_count = 0
        planned_visit_count = 0
        visited_customers_count = 0
        non_visited_count = 0
        emergency_supply_count = 0
        total_supplied_bottles = 0
        total_empty_bottles = 0
        total_count = 0
        stock_report_total = 0
        today_expense = 0
        today_payable = 0
        in_hand_amount = 0
        outstanding_closing_balance = 0
        credit_total_subtotal = 0
        cash_total_amount_recieved = 0
        credit_outstanding_collected_amount = 0
        todays_opening_outstanding_amount = 0
        collected_amount_from_custody_issue = 0
        foc_total_quantity = 0

        # ---- ROUTE, SALESMAN, VAN ----
        try:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            salesman = van_route.van.salesman
            self.stdout.write(f"Salesman: {salesman}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Route not found: {e}"))
            return

        # ---- CUSTOMERS ----
        new_customers_count = Customers.objects.filter(
            is_guest=False, created_date__date=date, sales_staff_id=salesman
        ).count()

        emergency_supply_count = DiffBottlesModel.objects.filter(
            created_date__date=date, assign_this_to_id=salesman
        ).count()

        visited_customers_count = CustomerSupply.objects.filter(
            salesman_id=salesman, created_date__date=date
        ).distinct().count()

        planned_visit_count = 0  # Adjust if find_customers() logic is added
        non_visited_count = planned_visit_count - visited_customers_count

        # ---- VAN STOCK ----
        van = Van.objects.get(salesman=salesman)
        van_product_stock = VanProductStock.objects.filter(
            created_date=date, van=van, product__product_name="5 Gallon"
        )

        stock_report_total = van_product_stock.aggregate(total_stock=Sum("stock"))["total_stock"] or 0
        total_empty_bottles = van_product_stock.aggregate(totalempty_bottle=Sum("empty_can_count"))["totalempty_bottle"] or 0
        total_supplied_bottles = van_product_stock.aggregate(total_sold=Sum("sold_count"))["total_sold"] or 0
        total_count = van_product_stock.aggregate(total_stock=Sum("stock"))["total_stock"] or 0

        # ---- CASH SALES ----
        cash_sales = CustomerSupply.objects.filter(
            created_date__date=date, salesman=salesman, amount_recieved__gt=0
        ).exclude(customer__sales_type="CASH COUPON")

        cash_total_amount_recieved = cash_sales.aggregate(total=Sum("amount_recieved"))["total"] or 0

        # ---- CREDIT SALES ----
        credit_sales = CustomerSupply.objects.filter(
            created_date__date=date, salesman=salesman, amount_recieved__lte=0
        ).exclude(customer__sales_type__in=["FOC", "CASH COUPON"])

        credit_total_subtotal = credit_sales.aggregate(total=Sum("subtotal"))["total"] or 0

        # ---- EXPENSES ----
        expenses = Expense.objects.filter(expense_date=date, van=van)
        today_expense = expenses.aggregate(total_expense=Sum("amount"))["total_expense"] or 0

        # ---- OUTSTANDING ----
        outstanding_amount_upto_yesterday = OutstandingAmount.objects.filter(
            customer_outstanding__product_type="amount",
            customer_outstanding__created_date__date__lt=date,
            customer_outstanding__customer__routes__route_name=route_name,
            customer_outstanding__customer__is_guest=False,
        ).aggregate(total_amount=Sum("amount"))["total_amount"] or 0

        dialy_collections = CollectionPayment.objects.filter(
            customer__routes__route_name=route_name, customer__is_guest=False
        )

        dialy_colection_upto_yesterday = dialy_collections.filter(
            created_date__date__lt=date
        ).aggregate(total_amount=Sum("amount_received"))["total_amount"] or 0

        todays_opening_outstanding_amount = outstanding_amount_upto_yesterday - dialy_colection_upto_yesterday
        credit_outstanding_collected_amount = dialy_collections.filter(
            created_date__date=date
        ).aggregate(total_amount=Sum("amount_received"))["total_amount"] or 0
        outstanding_closing_balance = todays_opening_outstanding_amount + credit_total_subtotal - credit_outstanding_collected_amount

        # ---- CUSTODY ----
        customer_custody_instances = CustodyCustom.objects.filter(
            created_date__date=date, customer__routes=van_route.routes
        )
        collected_amount_from_custody_issue = (
            customer_custody_instances.aggregate(total_amount=Sum("amount_collected"))["total_amount"] or 0
        )

        # ---- FOC ----
        foc_customers = CustomerSupply.objects.filter(
            created_date__date=date, customer__sales_type="FOC", salesman=salesman
        )
        for foc in foc_customers:
            foc_total_quantity += foc.get_total_supply_qty()

        # ---- OUTPUT SUMMARY ----
        self.stdout.write(self.style.SUCCESS("✅ DSR Summary"))
        self.stdout.write(f"Date: {date}")
        self.stdout.write(f"Route: {route_name}")
        self.stdout.write(f"New Customers: {new_customers_count}")
        self.stdout.write(f"Visited: {visited_customers_count} / Planned: {planned_visit_count} / Non-visited: {non_visited_count}")
        self.stdout.write(f"Emergency Supply Count: {emergency_supply_count}")
        self.stdout.write(f"Total Bottles Supplied: {total_supplied_bottles}")
        self.stdout.write(f"Total Empty Bottles: {total_empty_bottles}")
        self.stdout.write(f"Stock Total: {stock_report_total}")
        self.stdout.write(f"Cash Collected: ₹{cash_total_amount_recieved}")
        self.stdout.write(f"Credit Total: ₹{credit_total_subtotal}")
        self.stdout.write(f"Outstanding Opening: ₹{todays_opening_outstanding_amount}")
        self.stdout.write(f"Collected Today: ₹{credit_outstanding_collected_amount}")
        self.stdout.write(f"Outstanding Closing: ₹{outstanding_closing_balance}")
        self.stdout.write(f"Custody Collected: ₹{collected_amount_from_custody_issue}")
        self.stdout.write(f"FOC Quantity: {foc_total_quantity}")
        self.stdout.write(f"Today's Expense: ₹{today_expense}")
        self.stdout.write(self.style.SUCCESS("✅ Report generation completed."))
