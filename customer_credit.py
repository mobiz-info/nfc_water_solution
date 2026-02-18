import openpyxl
from decimal import Decimal
from django.db import transaction
from accounts.models import Customers






def import_customer_credit_from_excel(excel_path):
    """
    Reads Excel and inserts customer credit for NEGATIVE outstanding values.
    """

    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for row in sheet.iter_rows(min_row=2, values_only=True):

            customer_code = str(row[0]).strip()   # customer_id
            outstanding = Decimal(row[1] or 0)

            # We only care about CREDIT
            if outstanding >= 0:
                skipped_count += 1
                continue

            customer = Customers.objects.filter(custom_id=customer_code).first()
            if not customer:
                print(f"❌ Customer not found: {customer_code}")
                continue

            credit_amount = abs(outstanding)  # store as POSITIVE

            CustomerCredit.objects.create(
                customer=customer,
                amount=credit_amount,
                source="excel_import",
                remark="Imported customer credit from Excel"
            )

            created_count += 1
            print(f"✔ Credit added | Customer {customer_code} | Amount {credit_amount}")

    print("\n--- IMPORT SUMMARY ---")
    print("Credits created :", created_count)
    print("Rows skipped    :", skipped_count)
