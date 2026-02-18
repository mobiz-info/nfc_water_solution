import os
import django
import openpyxl
from datetime import date

# -----------------------------
# DJANGO SETUP
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  
django.setup()

from sales_management.models import CollectionPayment
from master.models import RouteMaster

ROUTE_NAME = "S-01"
START_DATE = date(2025, 12, 1)
END_DATE = date(2025, 12, 17)

OUTPUT_FILE = f"Route_{ROUTE_NAME}_Collection_{START_DATE}_to_{END_DATE}.xlsx"

# -----------------------------
# QUERY DATA
# -----------------------------
collections = CollectionPayment.objects.filter(
    customer__routes__route_name=ROUTE_NAME,
    created_date__date__range=(START_DATE, END_DATE)
).select_related("customer").order_by("created_date")

print(f"Total records found: {collections.count()}")

# -----------------------------
# CREATE EXCEL
# -----------------------------
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Route Collection Report"

# Header
ws.append([
    "Customer ID",
    "Customer Name",
    "Amount Received",
    "Created Date",
    "Receipt Number"
])

# Rows
for obj in collections:
    ws.append([
        obj.customer.custom_id,
        obj.customer.customer_name,
        float(obj.amount_received),
        obj.created_date.strftime("%Y-%m-%d"),
        obj.receipt_number or ""
    ])

# Save file
wb.save(OUTPUT_FILE)

print(f"✅ Excel file generated: {OUTPUT_FILE}")