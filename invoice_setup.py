import openpyxl

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from client_management.models import CustomerCredit
from invoice_management.models import Invoice
from accounts.models import Customers
from decimal import Decimal
from django.db import transaction
from datetime import date
from django.db.models import F

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
# EXCEL_FILE = "S18.xlsx"
# CUSTOMER_COL = 2        # custom_id column
# OUTSTANDING_COL = 5     # outstanding column
# START_ROW = 2           # skip header
# cutoff = date(2025, 12, 1)

# # -------------------------------------------------
# # LOAD EXCEL
# # -------------------------------------------------
# wb = openpyxl.load_workbook(EXCEL_FILE)
# sheet = wb.active

# print("\n🔄 Rebuilding invoices from Excel outstanding...\n")

# updated_customers = 0

# # -------------------------------------------------
# # PROCESS EACH CUSTOMER
# # -------------------------------------------------
# for row in sheet.iter_rows(min_row=START_ROW, values_only=True):

    

#     customer_code = str(row[CUSTOMER_COL - 1]).strip()


#     excel_outstanding = Decimal(row[OUTSTANDING_COL - 1] or 0)



#     print("excel_outstanding:",excel_outstanding)

#     customer = Customers.objects.filter(custom_id=customer_code).first()
#     if not customer:
#         print(f"❌ Customer not found: {customer_code}")
#         continue

    

#     if excel_outstanding < 0:
#             credit_amount = abs(excel_outstanding)

#             # Mark all invoices PAID
#             for inv in invoices:
#                 inv.amout_recieved = inv.amout_total
#                 inv.invoice_status = "paid"
#                 inv.save(update_fields=["amout_recieved", "invoice_status"])

#             # Save customer credit
#             CustomerCredit.objects.create(
#                 customer=customer,
#                 amount=credit_amount,
#                 source="excel_import",
#                 remark="Imported negative outstanding"
#             )

#             print(f"✅ Credit added: {credit_amount}")
#             continue

#     invoices = Invoice.objects.filter(
#         customer=customer,
#         is_deleted=False,
#         invoice_status = 'non_paid'
#         # created_date__date__lt=cutoff,
#     ).order_by("-created_date")

#     if not invoices.exists():
#         print(f"⚠ No invoices for customer {customer_code}")
#         continue

#     invoice_total_sum = sum(
#         Decimal(inv.amout_total or 0) for inv in invoices
#     )

#     paid_amount = invoice_total_sum - excel_outstanding
    
#     remaining_unpaid = excel_outstanding
    
#     with transaction.atomic():

       


#         for inv in invoices:
#             invoice_total = Decimal(inv.amout_total)

#             if remaining_unpaid <= 0:
#                 # fully paid
#                 inv.amout_recieved = invoice_total
#                 inv.invoice_status = "paid"
                
#             elif remaining_unpaid >= invoice_total:
#                 # fully unpaid
#                 inv.amout_recieved = Decimal("0.00")
#                 inv.invoice_status = "non_paid"
                
#                 remaining_unpaid -= invoice_total

#             else:
#                 # partially paid
#                 inv.amout_recieved = invoice_total - remaining_unpaid
#                 inv.invoice_status = "non_paid"
                
#                 remaining_unpaid = Decimal("0.00")

#             inv.save(update_fields=["amout_recieved", "invoice_status"])

#     updated_customers += 1
#     print(
#         f"✔ Customer {customer_code} rebuilt | "
#         f"Outstanding = {excel_outstanding}"
#     )

# # -------------------------------------------------
# # DONE
# # -------------------------------------------------
# print(f"\n🎉 DONE — Updated {updated_customers} customers\n")


def rebuild_customer_outstanding(
    customer_id,
    outstanding_amount,
    source="manual",
):
    """
    Rebuild invoices & credit for ONE customer
    """

    outstanding_amount = Decimal(outstanding_amount)

    customer = Customers.objects.filter(custom_id=customer_id).first()
    if not customer:
        raise ValueError("Customer not found")

    invoices = Invoice.objects.filter(
        customer=customer,
        is_deleted=False,
        invoice_type="credit_invoice",
    ).order_by("-created_date")

    if not invoices.exists():
        print(f"⚠ No invoices for customer {customer.custom_id}")
        return

    # ------------------ NEGATIVE OUTSTANDING ------------------
    if outstanding_amount < 0:
        credit_amount = abs(outstanding_amount)

        with transaction.atomic():

            # Mark all invoices paid
            for inv in invoices:
                inv.amout_recieved = inv.amout_total
                inv.invoice_status = "paid"
                inv.save(update_fields=["amout_recieved", "invoice_status"])

            # Save credit
            CustomerCredit.objects.create(
                customer=customer,
                amount=credit_amount,
                source=source,
                remark="Negative outstanding adjustment",
            )

        print(f"✅ Credit added for {customer.custom_id}: {credit_amount}")
        return

    # ------------------ POSITIVE OUTSTANDING ------------------
    remaining_unpaid = outstanding_amount

    with transaction.atomic():

        for inv in invoices:
            invoice_total = Decimal(inv.amout_total)

            if remaining_unpaid <= 0:
                inv.amout_recieved = invoice_total
                inv.invoice_status = "paid"

            elif remaining_unpaid >= invoice_total:
                inv.amout_recieved = Decimal("0.00")
                inv.invoice_status = "non_paid"
                remaining_unpaid -= invoice_total

            else:
                inv.amout_recieved = invoice_total - remaining_unpaid
                inv.invoice_status = "non_paid"
                remaining_unpaid = Decimal("0.00")

            inv.save(update_fields=["amout_recieved", "invoice_status"])

    print(
        f"✔ Customer {customer.custom_id} rebuilt | "
        f"Outstanding = {outstanding_amount}"
    )


rebuild_customer_outstanding(
    customer_id="5805",
    outstanding_amount=120.5
)


# CUTOFF_DATE = date(2025, 12, 1)
# DRY_RUN = False   # ⚠️ Set True to test without saving

# # -----------------------------------
# # CUSTOMER OUTSTANDING DATA
# # -----------------------------------
# # Format: customer_id : outstanding_amount

# CUSTOMER_OUTSTANDING = {
#     "7837": Decimal("401.5"),
#     # "CUST002": Decimal("0"),
#     # "CUST003": Decimal("120.75"),
#     # # add more here...
# }

# print("\n🔄 Updating customer outstanding...\n")

# updated = 0
# skipped = 0

# # -----------------------------------
# # PROCESS CUSTOMERS
# # -----------------------------------

# invoices = Invoice.objects.filter(
#         customer__routes__route_name="S-22",
#         is_deleted=False,
#         created_date__date__lt=CUTOFF_DATE
#     ).order_by("created_date")

# negative_invoices = invoices.filter(amout_total__lt=0)
# for inv in negative_invoices:
#         inv.amout_recieved = Decimal("0.00")
#         inv.amout_total = Decimal("0.00")
#         inv.invoice_status = "non_paid"
#         if not DRY_RUN:
#             inv.save(update_fields=["amout_recieved", "invoice_status","amout_total"])

# for customer_code, excel_outstanding in CUSTOMER_OUTSTANDING.items():

#     print("\n" + "=" * 50)
#     print(f"👤 Customer: {customer_code}")
#     print(f"📌 Expected Outstanding: {excel_outstanding}")
#     print("=" * 50)

#     customer = Customers.objects.filter(custom_id=customer_code).first()
#     if not customer:
#         print("❌ Customer not found")
#         continue

#     invoices = Invoice.objects.filter(
#         customer=customer,
#         is_deleted=False,
#         created_date__date__lt=CUTOFF_DATE
#     ).order_by("created_date")

#     if not invoices.exists():
#         print("⚠ No invoices before cutoff")
#         continue

#     total_invoice_amount = sum(
#         Decimal(inv.amout_total or 0) for inv in invoices
#     )

#     if excel_outstanding > total_invoice_amount:
#         print("❌ Outstanding is greater than total invoice amount")
#         continue

#     paid_amount = total_invoice_amount - excel_outstanding
#     remaining_unpaid = excel_outstanding

    

#     paid_invoices = []
#     unpaid_invoices = []
#     unpaid_total = Decimal("0.00")

#     positive_invoices = invoices.filter(amout_total__gt=0)
   

    


#     with transaction.atomic():
#         for inv in reversed(invoices):
#             invoice_total = Decimal(inv.amout_total)

#             if remaining_unpaid <= 0:
#                 # fully paid
#                 inv.amout_recieved = invoice_total
#                 inv.invoice_status = "paid"
#                 paid_invoices.append(inv.invoice_no)

#             elif remaining_unpaid >= invoice_total:
#                 # fully unpaid
#                 inv.amout_recieved = Decimal("0.00")
#                 inv.invoice_status = "non_paid"
#                 unpaid_invoices.append(inv.invoice_no)
#                 remaining_unpaid -= invoice_total

#             else:
#                 # partially paid
#                 inv.amout_recieved = invoice_total - remaining_unpaid
#                 inv.invoice_status = "non_paid"
#                 unpaid_invoices.append(inv.invoice_no)
#                 remaining_unpaid = Decimal("0.00")

#             inv.save(update_fields=["amout_recieved", "invoice_status"])


#     # for inv in negative_invoices:
#     #     inv.amout_recieved = Decimal("0.00")
        
#     #     if not DRY_RUN:
#     #         inv.save(update_fields=["amout_recieved", "invoice_status"])
#     # -----------------------------------
#     # PRINT SUMMARY
#     # -----------------------------------
#     print("\n✅ PAID INVOICES:")
#     for inv in paid_invoices:
#         print(f"   ✔ {inv}")

#     print("\n❌ UNPAID / PARTIALLY PAID INVOICES:")
#     for inv in unpaid_invoices:
#         print(f"   ✖ {inv}")

#     print(f"\n💰 TOTAL UNPAID AMOUNT: {unpaid_total}")

#     print("-" * 50)

# print("\n🎉 PROCESS COMPLETED\n")