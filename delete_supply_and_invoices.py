

import os
import django
from django.shortcuts import get_object_or_404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import transaction
from sales_management.models import CollectionPayment

from decimal import Decimal

from invoice_management.models import Invoice, InvoiceItems, InvoiceDailyCollection
from client_management.models import (
    CustomerOutstandingReport,
    CustomerSupply,
    CustomerOutstanding,
    OutstandingAmount,
)

def delete_customer_financials(customer_id):
    from accounts.models import Customers
    from invoice_management.models import Invoice
    from sales_management.models import CollectionPayment
    from client_management.models import (
        CustomerOutstanding,
        OutstandingAmount,
        OutstandingProduct,
        OutstandingCoupon,
        CustomerOutstandingReport,
    )

    customer = get_object_or_404(Customers, custom_id=customer_id)

    customer_name = customer.customer_name
    

    with transaction.atomic():

        # 1️⃣ Delete collections
        collection_count, _ = CollectionPayment.objects.filter(
            customer=customer
        ).delete()

        # 2️⃣ Delete outstanding amounts
        outstanding_amount_count, _ = OutstandingAmount.objects.filter(
            customer_outstanding__customer=customer
        ).delete()

        # 3️⃣ Delete outstanding products (empty cans)
        outstanding_product_count, _ = OutstandingProduct.objects.filter(
            customer_outstanding__customer=customer
        ).delete()

        # 4️⃣ Delete outstanding coupons
        outstanding_coupon_count, _ = OutstandingCoupon.objects.filter(
            customer_outstanding__customer=customer
        ).delete()

        # 5️⃣ Delete customer outstanding master
        customer_outstanding_count, _ = CustomerOutstanding.objects.filter(
            customer=customer
        ).delete()

        # 6️⃣ Delete invoices
        invoice_count, _ = Invoice.objects.filter(
            customer=customer
        ).delete()

        # 7️⃣ Delete outstanding report
        report_count, _ = CustomerOutstandingReport.objects.filter(
            customer=customer
        ).delete()

        supply_count, _ = CustomerSupply.objects.filter(
            customer = customer
        ).delete()

    print("🔥 CUSTOMER FINANCIAL RESET COMPLETED")
    print(f"👤 Customer : {customer_name} ")
    print(f"🧾 Invoices deleted            : {invoice_count}")
    print(f"💰 Collections deleted         : {collection_count}")
    print(f"📊 Outstanding amounts deleted : {outstanding_amount_count}")
    print(f"🧴 Outstanding products deleted: {outstanding_product_count}")
    print(f"🎟️ Outstanding coupons deleted : {outstanding_coupon_count}")
    print(f"📁 Outstanding master deleted  : {customer_outstanding_count}")
    print(f"📄 Report rows deleted         : {report_count}")
    print(f"📄 Supply deleted         : {supply_count}")

    return True

# # --------------------------------------------------
# # CONFIG — PUT YOUR INVOICE NUMBERS HERE
# # --------------------------------------------------
# INVOICE_NUMBERS = [
#    "IN-25/35679",   
# ]

# # --------------------------------------------------
# # MAIN FUNCTION
# # --------------------------------------------------
# def delete_invoices_and_related(invoice_numbers):
#     deleted_summary = {
#         "supplies": 0,
#         "outstanding_headers": 0,
#         "outstanding_amounts": 0,
#         "invoice_items": 0,
#         "invoice_daily_collections": 0,
#         "invoices": 0,
#     }

#     with transaction.atomic():

#         for invoice_no in invoice_numbers:
#             print(f"\n🔴 Processing invoice: {invoice_no}")

#             # -------------------------------
#             # Invoice
#             # -------------------------------
#             invoice = Invoice.objects.filter(
#                 invoice_no=invoice_no,
#                 is_deleted=False
#             ).first()

#             if not invoice:
#                 print("  ❌ Invoice not found, skipping")
#                 continue

#             customer = invoice.customer

#             # -------------------------------
#             # Customer Supply
#             # -------------------------------
#             supplies = CustomerSupply.objects.filter(invoice_no=invoice_no)
#             deleted_summary["supplies"] += supplies.count()
#             supplies.delete()
#             print("  ✔ CustomerSupply deleted")

#             # -------------------------------
#             # Outstanding (Amount)
#             # -------------------------------
#             outstanding_headers = CustomerOutstanding.objects.filter(
#                 customer=customer,
#                 invoice_no=invoice_no,
#                 product_type="amount"
#             )

#             for oh in outstanding_headers:
#                 oa_qs = OutstandingAmount.objects.filter(
#                     customer_outstanding=oh
#                 )
#                 deleted_summary["outstanding_amounts"] += oa_qs.count()
#                 oa_qs.delete()

#             deleted_summary["outstanding_headers"] += outstanding_headers.count()
#             outstanding_headers.delete()
#             print("  ✔ Outstanding records deleted")

#             # -------------------------------
#             # Invoice Items
#             # -------------------------------
#             invoice_items = InvoiceItems.objects.filter(invoice=invoice)
#             deleted_summary["invoice_items"] += invoice_items.count()
#             invoice_items.delete()

#             # -------------------------------
#             # Invoice Daily Collection
#             # -------------------------------
#             daily_collections = InvoiceDailyCollection.objects.filter(
#                 invoice=invoice
#             )
#             deleted_summary["invoice_daily_collections"] += daily_collections.count()
#             daily_collections.delete()

#             # -------------------------------
#             # Invoice
#             # -------------------------------
#             invoice.delete()
#             deleted_summary["invoices"] += 1
#             print("  ✔ Invoice deleted")

#         print("\n🎉 DELETE SUMMARY")
#         for k, v in deleted_summary.items():
#             print(f"{k}: {v}")

#     return deleted_summary


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    delete_customer_financials(19939)
