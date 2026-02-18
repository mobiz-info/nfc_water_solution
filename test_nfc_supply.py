import sys
import os
import django
import requests
import json
from datetime import datetime

# Setup Django environment - MUST BE FIRST
sys.path.append("/Users/muhammedanshid/Desktop/SanaTest")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "master.settings")
django.setup()

# Now import models
from django.contrib.auth import get_user_model
from bottle_management.models import Bottle
from master.models import ProdutItemMaster, CategoryMaster
from accounts.models import Customers, CustomUser
from van_management.models import Van
from client_management.models import SupplyItemBottle, CustomerSupply

User = get_user_model()

def test_nfc_supply():
    print("🚀 Starting NFC Supply Test...")

    # 1. Setup User (Salesman)
    username = "test_salesman_nfc"
    password = "password123"
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password, user_type="Salesman")
        print(f"   Created User: {username}")

    # 2. Setup Customer
    customer = Customers.objects.first()
    if not customer:
         print("❌ No customers found. Create one first.")
         return
    print(f"   Using Customer: {customer.customer_name} (ID: {customer.pk})")

    # 3. Setup Product (5 Gallon)
    product = ProdutItemMaster.objects.filter(product_name="5 Gallon").first()
    if not product:
        cat, _ = CategoryMaster.objects.get_or_create(category_name="Water")
        product = ProdutItemMaster.objects.create(product_name="5 Gallon", category=cat)
    print(f"   Using Product: {product.product_name}")

    # 4. Setup Bottles
    nfc_tags = ["NFC_TAG_ALPHA", "NFC_TAG_BETA"]
    for tag in nfc_tags:
        Bottle.objects.update_or_create(
            nfc_uid=tag,
            defaults={
                "serial_number": f"SN_{tag}",
                "product": product,
                "status": "VAN",
                "current_van": None, # Ideally we verify van logic too
            }
        )
    print(f"   Seeeded {len(nfc_tags)} bottles.")

    # 5. API Request
    url = "http://127.0.0.1:8000/api/create-customer-supply-nfc/"
    auth = (username, password)
    
    payload = {
        "customer": str(customer.pk),
        "salesman": str(user.pk),
        "nfc_tags": nfc_tags,
        # Default financial fields
        "grand_total": 0, "discount": 0, "net_payable": 0, "vat": 0, "subtotal": 0, "amount_recieved": 0,
        "reference_number": "REF_TEST_NFC_001",
        "collected_empty_bottle": 0,
        "allocate_bottle_to_pending": 0,
        "allocate_bottle_to_custody": 0,
        "allocate_bottle_to_paid": 0,
        "allocate_bottle_to_free": 0,
        "total_coupon_collected": 0,
        "vat_amount": 0,
        "amount_before_vat": 0,
        "payment_mode": "cash"
    }

    print(f"   Sending POST to {url}...")
    try:
        response = requests.post(url, json=payload, auth=auth)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            supply_id = data.get('supply_id')
            
            # Verify DB
            linked = SupplyItemBottle.objects.filter(supply_item__customer_supply__id=supply_id)
            print(f"   Mapped Bottles: {linked.count()}")
            for lb in linked:
                print(f"   - Bottle {lb.bottle.serial_number}: Status={lb.bottle.status} Customer={lb.bottle.current_customer}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_nfc_supply()
