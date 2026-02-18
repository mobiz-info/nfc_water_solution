import random
import math
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password
import pandas as pd
from decimal import Decimal
from accounts.models import CustomUser, Customers
from client_management.models import CustodyCustom, CustodyCustomItems, CustomerOutstanding, OutstandingAmount, CustomerOutstandingReport
from invoice_management.models import Invoice, InvoiceItems
from master.functions import get_custom_id
from master.models import BranchMaster, EmirateMaster, LocationMaster, RouteMaster
from product.models import ProdutItemMaster
from sales_management.models import CollectionPayment

# Read the Excel file
file_path = '/home/ra/Downloads/S-08 CUSTOMER ADD.xlsx'
data = pd.read_excel(file_path)

# Strip any leading/trailing whitespace from column names
data.columns = data.columns.str.strip()
# Verify that 'amount' column exists
# if 'amount' not in data.columns:
#     raise KeyError("Column 'amount' not found in the DataFrame. Available columns: " + ", ".join(data.columns))

# Assuming the excel columns are named as follows:
# 'customer_name', 'product_type', 'amount', 'created_by', 'modified_by'

def clean_value(value, default):
    """
    Check if the value is NaN and return the default value if it is.
    Otherwise, return the value itself.
    """
    if isinstance(value, float) and math.isnan(value):
        return default
    return value

@transaction.atomic
def populate_models_from_excel(data):
    user = CustomUser.objects.get(username="S-08")
    route = RouteMaster.objects.get(route_name="S-08")
    emirate = EmirateMaster.objects.get(name="Dubai")
    branch = BranchMaster.objects.get(name="Sana Water")
    # outstanding_in = CustomerOutstanding.objects.filter(customer__sales_staff=user,product_type='amount')
    # Invoice.objects.filter(customer__sales_staff=user).delete()
    # outstanding_in.delete()
    # CustomerOutstandingReport.objects.filter(customer__sales_staff=user,product_type='amount').delete()
    # CollectionPayment.objects.filter(salesman=user).delete()

    for index, row in data.iterrows():
        customer_id = clean_value(row['customer_code'], "")
        customer_name = clean_value(row['customer_name'], "")
        location, location_create = LocationMaster.objects.get_or_create(location_name=clean_value(row['location'], ""))
        customer_type = clean_value(row['customer_type'], "")
        sales_type = clean_value(row['sales_type'], "")
        phone_no = clean_value(row['phone_no'], "")
        building = clean_value(row['building'], "")
        room_no = clean_value(row['room_no'], "")
        floor_no = clean_value(row['floor_no'], "")
        bottle_rate = Decimal(clean_value(row['bottle_rate'], 0))  # Handle NaN and convert to Decimal
        custody_count = Decimal(clean_value(row['custody_count'], 0))  # Handle NaN and convert to Decimal
        outstanding = Decimal(clean_value(row['outstanding'], 0))  # Handle NaN and convert to Decimal
        day_of_supply = clean_value(row['day_of_supply'], "")
        
        print(type(phone_no),phone_no)
        
        if sales_type.lower() == "cash":
            sales_type = "CASH"
        if sales_type.lower() == "coupon":
            sales_type = "CASH COUPON"
        if sales_type.lower() == "foc":
            sales_type = "FOC"
            
        if customer_type.lower() == "home":
            customer_type = "HOME"
        if customer_type.lower() == "corporate":
            customer_type = "CORPORATE"
        if customer_type.lower() == "watchman":
            customer_type = "WATCHMAN"
        if customer_type.lower() == "shop":
            customer_type = "SHOP"
        
        # user_id = CustomUser.objects.none
        if phone_no != "":
            if not (user_id:=CustomUser.objects.filter(username=phone_no)).exists():
                user_id = user_id.first()
            else:
                user_id = CustomUser.objects.create(
                    username=phone_no,
                    password = make_password(str(phone_no))
                    )
                
        visit_schedule = {"Friday": [""], "Monday": [""], "Sunday": [""], "Tuesday": [], "Saturday": [], "Thursday": [], "Wednesday": []}
        if day_of_supply.lower() == "sunday":
            visit_schedule = {"Friday": [], "Monday": [], "Sunday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Tuesday": [], "Saturday": [], "Thursday": [], "Wednesday": []}
        if day_of_supply.lower() == "monday":
            visit_schedule = {"Friday": [], "Monday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Sunday": [], "Tuesday": [], "Saturday": [], "Thursday": [], "Wednesday": []}
        if day_of_supply.lower() == "tuesday":
            visit_schedule = {"Friday": [], "Monday": [], "Sunday": [], "Tuesday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Saturday": [], "Thursday": [], "Wednesday": []}
        if day_of_supply.lower() == "wednesday":
            visit_schedule = {"Friday": [], "Monday": [], "Sunday": [], "Tuesday": [], "Saturday": [], "Thursday": [], "Wednesday": ["Week1", "Week2", "Week3", "Week4", "Week5"]}
        if day_of_supply.lower() == "thursday":
            visit_schedule = {"Friday": [], "Monday": [], "Sunday": [], "Tuesday": [], "Saturday": [], "Thursday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Wednesday": []}
        if day_of_supply.lower() == "friday":
            visit_schedule = {"Friday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Monday": [], "Sunday": [], "Tuesday": [], "Saturday": [], "Thursday": [], "Wednesday": []}
        if day_of_supply.lower() == "saturday":
            visit_schedule = {"Friday": [], "Monday": [], "Sunday": [], "Tuesday": [], "Saturday": ["Week1", "Week2", "Week3", "Week4", "Week5"], "Thursday": [], "Wednesday": []}
        
        customer_instance = Customers.objects.create(
            created_by=1,
            created_date=datetime.today(),
            
            custom_id=get_custom_id(Customers),
            customer_name=customer_name,
            building_name=building,
            door_house_no=room_no,
            floor_no=floor_no,
            sales_staff=user,
            routes=route,
            location=location,
            emirate=emirate,
            mobile_no=phone_no,
            gps_latitude="0.0",
            gps_longitude="0.0",
            sales_type=sales_type,
            customer_type=customer_type,
            no_of_bottles_required=0,
            branch_id=branch,
            is_active=True,
            visit_schedule=visit_schedule,
            rate=bottle_rate
        )
        
        if phone_no != "":
            customer_instance.user_id=user_id
            customer_instance.save()
        
        if custody_count > 0:
            custodu_custom = CustodyCustom.objects.create(
                customer=customer_instance,
                total_amount=0,
                deposit_type="non_deposit",
                amount_collected=0
            )
            
            CustodyCustomItems.objects.create(
                custody_custom=custodu_custom,
                product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                quantity=custody_count,
                serialnumber=0,
                amount=0,
                can_deposite_chrge=0,
                five_gallon_water_charge=customer_instance.rate,
            )
            
        if outstanding > 0:
            customer_outstanding = CustomerOutstanding.objects.create(
                customer=customer_instance,
                product_type='amount',
                created_by=user.id,
                modified_by=user.id,
                created_date=customer_instance.created_date,
            )

            # Create OutstandingAmount
            outstanding_amount = OutstandingAmount.objects.create(
                customer_outstanding=customer_outstanding,
                amount=outstanding
            )

            # Update or create CustomerOutstandingReport
            if (instances:=CustomerOutstandingReport.objects.filter(customer=customer_instance,product_type='amount')).exists():
                report = instances.first()
            else:
                report = CustomerOutstandingReport.objects.create(customer=customer_instance,product_type='amount')

            report.value += outstanding
            report.save()
            
            # Create the invoice
            invoice = Invoice.objects.create(
                created_date=outstanding_amount.customer_outstanding.created_date,
                net_taxable=outstanding_amount.amount,
                vat=0,
                discount=0,
                amout_total=outstanding_amount.amount,
                amout_recieved=0,
                customer=outstanding_amount.customer_outstanding.customer,
                reference_no=f"custom_id{outstanding_amount.customer_outstanding.customer.custom_id}"
            )
            customer_outstanding.invoice_no = invoice.invoice_no
            customer_outstanding.save()
            
            if outstanding_amount.customer_outstanding.customer.sales_type == "CREDIT":
                invoice.invoice_type = "credit_invoice"
                invoice.save()

            # Create invoice items
            item = ProdutItemMaster.objects.get(product_name="5 Gallon")
            water_rate = outstanding_amount.customer_outstanding.customer.get_water_rate()
            InvoiceItems.objects.create(
                category=item.category,
                product_items=item,
                qty=0,
                rate=water_rate,
                invoice=invoice,
                remarks='invoice genereted from backend reference no : ' + invoice.reference_no
            )

        print(f"Processed row {index + 1} for customer {customer_id}")

# Execute the function
populate_models_from_excel(data)
