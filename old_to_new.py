import os
import django
from datetime import date, datetime
from django.utils.timezone import make_aware
from django.db import connections, transaction





os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from invoice_management.models import Invoice
from accounts.models import Customers
from client_management.models import CustomerOutstanding, OutstandingAmount

# # ---------------- CONFIG ----------------
# ROUTE_CODE = "S-31"


# OLD_DB = "old_db"
# NEW_DB = "default"


# START_DATE = make_aware(datetime(2025, 3, 1))
# END_DATE = make_aware(datetime(2025, 12, 31, 22, 59, 59))

# # 2. Use .using() to target the old database
# count = CustomerOutstanding.objects.using(OLD_DB).filter(
#     created_date__range=(START_DATE, END_DATE)
# ).count()

# print(f"--- Database: {OLD_DB} ---")
# print(f"Outstanding row count for Salesman 827: {count}")




# start_date = datetime(2025, 3, 1)
# end_date = datetime(2025, 12, 31, 23, 59, 59)


# def sync_and_cleanup_data():
#     # 1. Configuration
#     ROUTE_NAME = "S-31" 
#     OLD_DB = "old_db"
#     NEW_DB = "default"
    
#     START_DATE = make_aware(datetime(2025, 3, 1, 0, 0, 0))
#     END_DATE = make_aware(datetime(2025, 12, 31, 23, 59, 59))

#     print(f"--- Starting Exact Sync for Route {ROUTE_NAME} ---")

#     # 2. Get Source of Truth (IDs that MUST exist)
#     print("Identifying Source of Truth IDs from Old DB...")
#     old_co_ids = set(CustomerOutstanding.objects.using(OLD_DB).filter(
#         created_date__range=(START_DATE, END_DATE),
#         customer__routes__route_name=ROUTE_NAME
#     ).values_list('id', flat=True))

#     old_oa_ids = set(OutstandingAmount.objects.using(OLD_DB).filter(
#         customer_outstanding__created_date__range=(START_DATE, END_DATE),
#         customer_outstanding__customer__routes__route_name=ROUTE_NAME
#     ).values_list('id', flat=True))

#     with transaction.atomic(using=NEW_DB):
#         # --- PHASE 1: DELETE ORPHANS (Data in New not in Old) ---
#         print("\nChecking for records to delete in New DB...")
        
#         # Delete orphan OutstandingAmount records first (Child table)
#         oa_to_delete = OutstandingAmount.objects.using(NEW_DB).filter(
#             customer_outstanding__created_date__range=(START_DATE, END_DATE),
#             customer_outstanding__customer__routes__route_name=ROUTE_NAME
#         ).exclude(id__in=old_oa_ids)
        
#         oa_del_count = oa_to_delete.count()
#         if oa_del_count > 0:
#             oa_to_delete.delete()
#             print(f"🗑️ Deleted {oa_del_count} orphan amount records.")

#         # Delete orphan CustomerOutstanding records (Parent table)
#         co_to_delete = CustomerOutstanding.objects.using(NEW_DB).filter(
#             created_date__range=(START_DATE, END_DATE),
#             customer__routes__route_name=ROUTE_NAME
#         ).exclude(id__in=old_co_ids)
        
#         co_del_count = co_to_delete.count()
#         if co_del_count > 0:
#             co_to_delete.delete()
#             print(f"🗑️ Deleted {co_del_count} orphan header records.")

#         # --- PHASE 2: SYNC MISSING DATA (Data in Old not in New) ---
#         print("\nChecking for missing records to add to New DB...")
        
#         # Get existing IDs in New DB now
#         current_co_ids = set(CustomerOutstanding.objects.using(NEW_DB).values_list('id', flat=True))
#         current_oa_ids = set(OutstandingAmount.objects.using(NEW_DB).values_list('id', flat=True))

#         # Sync Headers
#         headers_to_add = [
#             rec for rec in CustomerOutstanding.objects.using(OLD_DB).filter(
#                 id__in=old_co_ids
#             ) if rec.id not in current_co_ids
#         ]
        
#         if headers_to_add:
#             CustomerOutstanding.objects.using(NEW_DB).bulk_create(headers_to_add, batch_size=500)
#             print(f"✅ Added {len(headers_to_add)} missing headers.")

#         # Sync Amounts
#         amounts_to_add = [
#             amt for amt in OutstandingAmount.objects.using(OLD_DB).filter(
#                 id__in=old_oa_ids
#             ) if amt.id not in current_oa_ids
#         ]
        
#         if amounts_to_add:
#             OutstandingAmount.objects.using(NEW_DB).bulk_create(amounts_to_add, batch_size=500)
#             print(f"✅ Added {len(amounts_to_add)} missing amounts.")

#     print(f"\n✨ SUCCESS: New DB is now an exact mirror of Old DB for Route {ROUTE_NAME} within the date range.")

# sync_and_cleanup_data()

# OLD_SALESMAN_ID = 827  # Ismail
# NEW_SALESMAN_ID = 950  # New Salesman
# TARGET_ROUTE = "S-31"  # Only move data for this route

# # Define the Date Range (Jan 1 to Jan 3)
# start_date = make_aware(datetime(2026, 1, 1, 0, 0, 0))
# end_date = make_aware(datetime(2026, 1, 3, 23, 59, 59))

# def run_salesman_migration_by_route():
#     try:
#         with transaction.atomic():
#             print(f"Migrating Route {TARGET_ROUTE} from ID {OLD_SALESMAN_ID} to ID {NEW_SALESMAN_ID}...")

#             # 2. UPDATE WITH ROUTE FILTER
#             # We filter by salesman AND date AND route_name
            
#             inv_count = Invoice.objects.filter(
#                 salesman_id=OLD_SALESMAN_ID,
#                 created_date__range=(start_date, end_date),
#                 customer__routes__route_name=TARGET_ROUTE
#             ).update(salesman_id=NEW_SALESMAN_ID)

#             out_count = CustomerOutstanding.objects.filter(
#                 created_by = OLD_SALESMAN_ID,
#                 created_date__range=(start_date, end_date),
                
#             ).update(salesman_id=NEW_SALESMAN_ID)

#             sup_count = Supply.objects.filter(
#                 salesman_id=OLD_SALESMAN_ID,
#                 created_date__range=(start_date, end_date),
#                 customer__routes__route_name=TARGET_ROUTE
#             ).update(salesman_id=NEW_SALESMAN_ID)

#             print("-" * 30)
#             print(f"✅ Migration Successful for Route {TARGET_ROUTE}!")
#             print(f"Invoices updated:    {inv_count}")
#             print(f"Outstandings updated: {out_count}")
#             print(f"Supply records updated: {sup_count}")
#             print("-" * 30)
#             print("Note: Data before Jan 1 (Dec 30) remains with the old salesman.")

#     except Exception as e:
#         print(f"❌ Error during migration: {e}")

# # Execute
# run_salesman_migration_by_route()


from django.db import transaction
from django.utils.timezone import make_aware
from datetime import datetime

from invoice_management.models import (
    Invoice,
    InvoiceDailyCollection,
    SuspenseCollection,
)
from client_management.models import CustomerSupply, CustomerOutstanding
from sales_management.models import CollectionPayment
from order.models import Order
from django.db.models import Sum






from django.db import transaction
from django.utils.timezone import make_aware
from datetime import datetime

# qs = CustomerOutstanding.objects.filter(
#     customer__routes__route_name="S-18",
#     created_date__date=date(2025, 9, 1),  # ONLY Sep 1
#     created_by="822",                     # current salesman
#     outstandingamount__amount__lt=0       # NEGATIVE outstanding
# ).distinct()



# print("Records to update:", qs.count())

# for obj in qs[:10]:
#     print(
#         obj.customer.custom_id,
#         obj.created_date,
#         obj.created_by,
#         obj.outstandingamount_set.first().amount
#     )

# with transaction.atomic():
#     updated = qs.update(created_by="2380")

# print("Updated records:", updated)


# def migrate_salesman_with_preview(
   
#     new_salesman_id: int,
#     route_name: str,
#     end_date: datetime,
#     do_update: bool = False,
# ):
#     """
#     Update all records of a route BEFORE a given date
#     """

#     end_date = make_aware(end_date)

#     print("\n" + "=" * 70)
#     print("🔍 SALESMAN MIGRATION PREVIEW")
#     print("=" * 70)
#     print(f"Route      : {route_name}")
    
#     print(f"To         : {new_salesman_id}")
#     print(f"Before     : {end_date}")
#     print("-" * 70)

#     # -------------------- FILTERED QUERYSETS --------------------
#     invoice_qs = Invoice.objects.filter(
#         # salesman_id=471,
#         #  salesman_id = new_salesman_id,
#         created_date__lte=end_date,
#         customer__routes__route_name=route_name
#     )

#     supply_qs = CustomerSupply.objects.filter(
#         # salesman_id=471,
#         created_date__lte=end_date,
#         #  salesman_id = new_salesman_id,
#         customer__routes__route_name=route_name
#     )

#     collection_qs = CollectionPayment.objects.filter(
#         # salesman_id=471,
#         #  salesman_id = new_salesman_id,
#         created_date__lte=end_date,
#         customer__routes__route_name=route_name
#     )

#     daily_collection_qs = InvoiceDailyCollection.objects.filter(
#         # salesman_id=471,
#         #  salesman_id = new_salesman_id,
#         created_date__lte=end_date,
#         invoice__customer__routes__route_name=route_name
#     )

#     suspense_qs = SuspenseCollection.objects.filter(
    
#     created_date__lte=end_date,
#     route__route_name=route_name
#     )

#     order_qs = Order.objects.filter(
    
#     order_date__lte=end_date.date(),   # 👈 use order_date
#     route__route_name=route_name
# )

#     outstanding_qs = CustomerOutstanding.objects.filter(
        
#         created_date__lte=end_date,
#         customer__routes__route_name=route_name
#     )

#     # -------------------- PREVIEW COUNTS --------------------
#     print(f"Invoices                     : {invoice_qs.count()}")
#     print(f"CustomerSupply               : {supply_qs.count()}")
#     print(f"CollectionPayment            : {collection_qs.count()}")
#     print(f"InvoiceDailyCollection       : {daily_collection_qs.count()}")
#     print(f"SuspenseCollection           : {suspense_qs.count()}")
#     print(f"Orders                       : {order_qs.count()}")
#     print(f"CustomerOutstanding(created) : {outstanding_qs.count()}")

#     print("-" * 70)

#     if not do_update:
#         print("🟡 DRY-RUN ONLY — NO DATA UPDATED")
#         print("➡️  Re-run with do_update=True to apply")
#         print("=" * 70)
#         return

#     # -------------------- APPLY UPDATE --------------------
#     with transaction.atomic():

#         print("\n🚀 APPLYING UPDATES...\n")

#         print("Invoices updated               :", invoice_qs.update(salesman_id=new_salesman_id))
#         print("CustomerSupply updated         :", supply_qs.update(salesman_id=new_salesman_id))
#         print("CollectionPayment updated      :", collection_qs.update(salesman_id=new_salesman_id))
#         print("InvoiceDailyCollection updated :", daily_collection_qs.update(salesman_id=new_salesman_id))
#         print("SuspenseCollection updated     :", suspense_qs.update(salesman_id=new_salesman_id))
#         print("Orders updated                 :", order_qs.update(salesman_id=new_salesman_id))
#         print("CustomerOutstanding updated    :", outstanding_qs.update(created_by=str(new_salesman_id)))

#         print("\n✅ UPDATE COMPLETED SUCCESSFULLY")
#         print("=" * 70)


# migrate_salesman_with_preview(
#     new_salesman_id=2380,      # 👈 new salesman
#     route_name="S-18",
#     end_date=datetime(2026, 8, 31, 23, 59, 59),
#     do_update=True            # 👈 PREVIEW ONLY
# )
