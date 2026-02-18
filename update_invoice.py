
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from client_management.models import CustomerCredit, CustomerOutstanding, CustomerSupply
from invoice_management.models import Invoice
from accounts.models import Customers
from decimal import Decimal
from django.db import transaction
from datetime import date
from django.db.models import F

from collections import defaultdict
from invoice_management.models import Invoice
from django.db import transaction

# group invoices by invoice_no
# invoice_map = defaultdict(list)

# for inv in Invoice.objects.order_by("invoice_no", "id"):
#     invoice_map[inv.invoice_no].append(inv)

# with transaction.atomic():
#     for invoice_no, invoices in invoice_map.items():
#         if len(invoices) > 1:
#             # keep first as-is
#             for index, inv in enumerate(invoices[1:], start=1):
#                 new_invoice_no = f"{invoice_no}-{index}"
#                 inv.invoice_no = new_invoice_no
#                 inv.save(update_fields=["invoice_no"])
#                 print(f"Updated: {invoice_no} → {new_invoice_no}")


from django.db.models import F

today = date.today()
outstanding_day = date(2026, 1, 1)   # Jan 1

# qs = CustomerOutstanding.objects.filter(
#     outstanding_date__date=outstanding_day,
#     created_date__date=today,
#     customer__routes__route_name="S3",
#     outstandingamount__amount__lt=0
# )

# print("Records to update:", qs.count())
# print(qs.values("id", "created_by"))

updated_count = CustomerOutstanding.objects.filter(
    outstanding_date__date=outstanding_day,
    created_date__date=today,
    customer__routes__route_name="S-03",
    outstandingamount__amount__lt=0   # ✅ from OutstandingAmount model
).update(
    created_by="891"
)

# TEST_ROUTE_NAME = "test_route2"

# supply_updated = CustomerSupply.objects.filter(
#     supply_date__isnull=True,
# ).update(
#     supply_date=F('created_date')
# )

# invoice_updated = Invoice.objects.filter(
#     invoice_date__isnull=True,
#     # customer__routes__route_name=TEST_ROUTE_NAME
# ).update(
#     invoice_date=F('created_date')
# )

# outstanding_updated = CustomerOutstanding.objects.filter(
#     outstanding_date__isnull=True,
#     # customer__routes__route_name=TEST_ROUTE_NAME
# ).update(
#     outstanding_date=F('created_date')
# )

# print("Updated supply rows:", supply_updated)
# print("Updated invoice rows:", invoice_updated)
# print("Updated outstanding rows:", outstanding_updated)
