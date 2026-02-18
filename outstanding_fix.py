from decimal import Decimal
import os
import django
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Sum

# -------------------------------------------------
# DJANGO SETUP
# -------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # adjust if needed
django.setup()

# -------------------------------------------------
# IMPORT MODELS
# -------------------------------------------------
from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount
from accounts.models import Customers

# -------------------------------------------------
# INPUTS (CHANGE THESE)
# -------------------------------------------------
# CUSTOMER_ID = "16501"   # custom_id OR use pk
# START_DATE = make_aware(datetime(2025, 11, 10))
# END_DATE = make_aware(datetime(2025, 11, 30, 22, 59, 59))

# # -------------------------------------------------
# # GET CUSTOMER
# # -------------------------------------------------
# customer = Customers.objects.filter(custom_id=CUSTOMER_ID).first()

# if not customer:
#     print(f"❌ Customer not found: {CUSTOMER_ID}")
#     exit()

# print(f"\nChecking invoices for customer: {customer}")
# print(f"Period: {START_DATE.date()} to {END_DATE.date()}\n")

# invoices = Invoice.objects.filter(
#     customer=customer,
#     created_date__range=(START_DATE, END_DATE),
# #     invoice_type = "credit_invoice",
#     is_deleted=False
# )

# updated_count = 0

# # ------------------------------------
# # ONLY UPDATE OutstandingAmount
# # ------------------------------------
# for inv in invoices:
#     invoice_total = Decimal(inv.amout_total or 0)

#     co = CustomerOutstanding.objects.filter(
#         customer=customer,
#         invoice_no=inv.invoice_no,
#         product_type="amount"
#     ).first()

#     if not co:
#         continue  # ❌ do nothing

#     oa = OutstandingAmount.objects.filter(
#         customer_outstanding=co
#     ).first()

#     if not oa:
#         continue  # ❌ do nothing

#     # ✅ ONLY UPDATE amount
#     if Decimal(oa.amount) != invoice_total:
#         oa.amount = invoice_total
#         oa.save(update_fields=["amount"])
#         updated_count += 1
#         print(f"🔧 UPDATED {inv.invoice_no} → {invoice_total}")

# # ------------------------------------
# # DONE
# # ------------------------------------
# print(f"\n🎉 Finished. Total OutstandingAmount updated: {updated_count}\n")


# CUSTOMER_CODE = "7637"
# REPORT_DATE = make_aware(datetime(2025, 11, 30))
# data = (
#     OutstandingAmount.objects
#     .filter(
#         customer_outstanding__customer__custom_id=CUSTOMER_CODE,
#         customer_outstanding__created_date__date__lte=REPORT_DATE
#     )
#     .select_related("customer_outstanding")
#     .values(
#         "customer_outstanding__created_date",
#         "customer_outstanding__invoice_no"
#     )
#     .annotate(
#         amount=Sum("amount")
#     )
#     .order_by("customer_outstanding__created_date")
# )
# total_outstanding = sum(row["amount"] for row in data)

# print("Date       | Invoice No           | Outstanding Amount")
# print("------------------------------------------------------")

# for row in data:
#     print(
#         row["customer_outstanding__created_date"].date(),
#         "|",
#         row["customer_outstanding__invoice_no"],
#         "|",
#         row["amount"]
#     )

# print("Total Outstanding Amount:", total_outstanding)


# Route wise OutstandingAmount fix---------------------------------------------------------------------------------

ROUTE_NAME = "V-5"   # or use route_id
START_DATE = make_aware(datetime(2025, 1, 1))
END_DATE = make_aware(datetime(2025, 12, 18, 22, 59, 59))

# -------------------------------------------------
# GET CUSTOMERS IN ROUTE
# -------------------------------------------------
customers = Customers.objects.filter(
    routes__route_name=ROUTE_NAME,
    is_deleted=False
)

if not customers.exists():
    print(f"❌ No customers found for route {ROUTE_NAME}")
    exit()

print(f"\nProcessing route: {ROUTE_NAME}")
print(f"Period: {START_DATE.date()} to {END_DATE.date()}")
print(f"Total customers: {customers.count()}\n")

updated_count = 0
skipped_count = 0

# -------------------------------------------------
# PROCESS EACH CUSTOMER
# -------------------------------------------------
for customer in customers:

    invoices = Invoice.objects.filter(
        customer=customer,
        created_date__range=(START_DATE, END_DATE),
        invoice_type = "credit_invoice",
        is_deleted=False
    )

    if not invoices.exists():
        continue

    for inv in invoices:

        invoice_total = Decimal(inv.amout_total or 0)

        co = CustomerOutstanding.objects.filter(
            customer=customer,
            invoice_no=inv.invoice_no,
            product_type="amount"
        ).first()

        if not co:
            skipped_count += 1
            continue

        oa = OutstandingAmount.objects.filter(
            customer_outstanding=co
        ).first()

        if not oa:
            skipped_count += 1
            continue

        # ✅ ONLY UPDATE OutstandingAmount.amount
        if Decimal(oa.amount) != invoice_total:
            oa.amount = invoice_total
            oa.save(update_fields=["amount"])
            updated_count += 1
            print(
                f"🔧 {customer.custom_id} | "
                f"{inv.invoice_no} → {invoice_total}"
            )

# -------------------------------------------------
# DONE
# -------------------------------------------------
print("\n🎉 FINISHED")
print(f"✅ Updated OutstandingAmount rows: {updated_count}")
print(f"⚠️ Skipped (missing data): {skipped_count}\n")



# CUSTOMER_ID = "7821"   # custom_id OR use pk
# START_DATE = make_aware(datetime(2025, 10, 1))
# END_DATE = make_aware(datetime(2025, 11, 30, 22, 59, 59))

# # -------------------------------------------------
# # GET CUSTOMER
# # -------------------------------------------------
# customer = Customers.objects.filter(custom_id=CUSTOMER_ID).first()

# if not customer:
#     print(f"❌ Customer not found: {CUSTOMER_ID}")
#     exit()

# print(f"\nChecking invoices for customer: {customer}")
# print(f"Period: {START_DATE.date()} to {END_DATE.date()}\n")

# invoices = Invoice.objects.filter(
#     customer=customer,
#     created_date__range=(START_DATE, END_DATE),
# #     invoice_type = "credit_invoice",
#     is_deleted=False
# )

# updated_count = 0

# # ------------------------------------
# # ONLY UPDATE OutstandingAmount
# # ------------------------------------
# for inv in invoices:
#     invoice_total = Decimal(inv.amout_total or 0)

#     co = CustomerOutstanding.objects.filter(
#         customer=customer,
#         invoice_no=inv.invoice_no,
#         product_type="amount"
#     ).first()

#     if not co:
#         continue  # ❌ do nothing

#     oa = OutstandingAmount.objects.filter(
#         customer_outstanding=co
#     ).first()

#     if not oa:
#         continue  # ❌ do nothing

#     # ✅ ONLY UPDATE amount
#     if Decimal(oa.amount) != invoice_total:
#         oa.amount = invoice_total
#         oa.save(update_fields=["amount"])
#         updated_count += 1
#         print(f"🔧 UPDATED {inv.invoice_no} → {invoice_total}")

# # ------------------------------------
# # DONE
# # ------------------------------------
# print(f"\n🎉 Finished. Total OutstandingAmount updated: {updated_count}\n")





start_date = make_aware(datetime(2025, 12, 1))
end_date = make_aware(datetime(2025, 12, 18, 23, 59, 59))

route = "S-22"

invoices = Invoice.objects.filter(
    created_date__range=(start_date, end_date),
    customer__routes__route_name=route,
    is_deleted=False
)

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

        print(
            f"Updated {invoice_no}: {old_amount} → {invoice_amount}"
        )

print(
    f"\nFinished! Updated {updated_count} outstanding amount records for route all."
)