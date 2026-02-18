from django.forms import ValidationError
from django.shortcuts import render
from datetime import datetime
from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from product.models import ProdutItemMaster
from .models import Product, Bottle
import json
import re

from bottle_management.models import Bottle, BottleLedger
import base64
from django.contrib.auth import authenticate

# Create your views here.

def get_last_number(date_str, prefix):
    regex = rf"^{date_str}-{prefix}(\d+)$"
    
    # Fetch all matching serial numbers
    serials = Bottle.objects.filter(serial_number__regex=regex).values_list('serial_number', flat=True)
    
    max_number = 0
    
    for serial in serials:
        match = re.search(r"(\d+)$", serial)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
                
    return max_number

@transaction.atomic
def generate_bottles(
    *,
    product,
    quantity,
    prefix="BTL",
    created_by=None
):
    """
    Generates bottles with serial numbers
    """

    today = datetime.now()
    date_str = today.strftime("%d-%m")

    last_number = get_last_number(prefix, date_str)

    bottles = []
    ledgers = []

    for i in range(1, quantity + 1):
        serial = f"{date_str}-{prefix}{last_number + i}"

        bottle = Bottle(
            serial_number=serial,
            product=product,
            status="GODOWN"
        )
        bottles.append(bottle)

    Bottle.objects.bulk_create(bottles)

    for bottle in bottles:
        ledgers.append(
            BottleLedger(
                bottle=bottle,
                action="CREATE",
                reference=f"initial_stock_{date_str}"
            )
        )

    BottleLedger.objects.bulk_create(ledgers)

    return bottles


@csrf_exempt
def preview_bottles(request):
    data = json.loads(request.body)
    qty = int(data["qty"])
    prefix = data.get("prefix", "BTL")

    today = datetime.now().strftime("%d-%m")
    last_no = get_last_number(today, prefix)

    serials = [
        f"{today}-{prefix}{last_no + i}"
        for i in range(1, qty + 1)
    ]

    return JsonResponse({"serials": serials})


def bottle_generator_page(request):
    products = ProdutItemMaster.objects.exclude(
    category__category_name__icontains="coupon"
    )
    return render(request, "bottle_management/generate_bottle.html", {"products": products})


@csrf_exempt
def save_bottles(request):
    data = json.loads(request.body)

    product_id = data["product_id"]
    serials = data["serials"]

    product = ProdutItemMaster.objects.get(id=product_id)

    result = save_generated_bottles(
        product=product,
        serials=serials
    )

    return JsonResponse(result, status=201)

@transaction.atomic
def save_generated_bottles(*, product, serials, created_by=None):
    """
    Save generated bottle serial numbers into DB
    """

    if not serials:
        raise ValidationError("No serial numbers provided")

    # 1️⃣ Prevent duplicates
    existing = set(
        Bottle.objects.filter(
            serial_number__in=serials
        ).values_list("serial_number", flat=True)
    )

    if existing:
        raise ValidationError(
            f"Serials already exist: {', '.join(existing)}"
        )

    # 2️⃣ Bulk create bottles (NO FK usage yet)
    Bottle.objects.bulk_create([
        Bottle(
            serial_number=serial,
            product=product,
            status="GODOWN"
        )
        for serial in serials
    ])

    # 3️⃣ Re-fetch bottles WITH IDs
    created_bottles = Bottle.objects.filter(
        serial_number__in=serials
    )

    # 4️⃣ Create ledger entries
    BottleLedger.objects.bulk_create([
        BottleLedger(
            bottle=bottle,
            action="CREATE",
            reference="initial_stock",
          #   created_by=created_by
        )
        for bottle in created_bottles
    ])

    return {
        "created_count": len(created_bottles),
        "serials": serials
    }

@transaction.atomic
def map_nfc_to_bottle(*, bottle_id, nfc_uid, created_by=None):
    """
    Map NFC UID to a bottle (one-time operation)
    """

    nfc_uid = nfc_uid.strip()

    if not nfc_uid:
        raise ValidationError("NFC UID is required")

    
    if Bottle.objects.filter(nfc_uid=nfc_uid).exists():
        raise ValidationError("This NFC UID is already mapped to another bottle")

    
    bottle = Bottle.objects.select_for_update().get(id=bottle_id)

    
    if bottle.nfc_uid:
        raise ValidationError("This bottle already has NFC mapped")

    
    bottle.nfc_uid = nfc_uid
    bottle.save()

    
    BottleLedger.objects.create(
        bottle=bottle,
        action="MAP_NFC",
        reference=nfc_uid,
        created_by=created_by
    )

    return {
        "bottle": bottle.serial_number,
        "nfc_uid": nfc_uid,
        "status": "MAPPED"
    }


@csrf_exempt
def nfc_mapping_save(request):
    try:
        data = json.loads(request.body)

        bottle_id = data.get("bottle_id")
        nfc_uid = data.get("nfc_uid")

        user = request.user
        if not user.is_authenticated:
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2 and auth[0].lower() == "basic":
                    try:
                        username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
                        user = authenticate(username=username, password=password)
                    except Exception:
                        pass

        result = map_nfc_to_bottle(
            bottle_id=bottle_id,
            nfc_uid=nfc_uid,
            created_by=user if user and user.is_authenticated else None
        )

        return JsonResponse(result, status=200)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def nfc_mapping_page(request):
    bottles = Bottle.objects.filter(nfc_uid__isnull=True)
    return render(
        request,
        "bottle_management/nfc_mapping.html",
        {"bottles": bottles}
    )

def get_available_bottles(request):
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({"error": "Product ID is required"}, status=400)
    
    bottles = Bottle.objects.filter(product_id=product_id, status="GODOWN", nfc_uid__isnull=True)
    data = [{"id": str(b.id), "serial_number": b.serial_number} for b in bottles]
    
    return JsonResponse({"bottles": data})


@transaction.atomic
def generate_bottles_with_nfc(
    *,
    product,
    nfc_uids,
    prefix="BTL",
    created_by=None
):
    """
    Generates bottles with serial numbers and assigns NFC UIDs
    """

    if not nfc_uids:
        raise ValidationError("No NFC UIDs provided")
    
    # Check for duplicate NFCs
    existing_nfcs = Bottle.objects.filter(nfc_uid__in=nfc_uids).values_list('nfc_uid', flat=True)
    if existing_nfcs:
        raise ValidationError(f"NFC UIDs already mapped: {', '.join(existing_nfcs)}")

    today = datetime.now()
    date_str = today.strftime("%d-%m")

    last_number = get_last_number(date_str, prefix)

    bottles = []
    ledgers = []

    for i, nfc_uid in enumerate(nfc_uids):
        serial = f"{date_str}-{prefix}{last_number + i + 1}"

        bottle = Bottle(
            serial_number=serial,
            product=product,
            status="GODOWN",
            nfc_uid=nfc_uid,
            qr_code=serial  # Use serial number as QR code
        )
        bottles.append(bottle)

    Bottle.objects.bulk_create(bottles)

    # Re-fetch to get IDs for ledger
    created_bottles = Bottle.objects.filter(serial_number__in=[b.serial_number for b in bottles])

    for bottle in created_bottles:
        ledgers.append(
            BottleLedger(
                bottle=bottle,
                action="CREATE_WITH_NFC",
                reference=f"initial_stock_{date_str}",
                created_by=created_by
            )
        )

    BottleLedger.objects.bulk_create(ledgers)

    return bottles


@csrf_exempt
def generate_bottles_with_nfc_api(request):
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        nfc_uids = data.get("nfc_uids")

        if not product_id:
            return JsonResponse({"error": "Product ID is required"}, status=400)
        
        if not nfc_uids or not isinstance(nfc_uids, list):
            return JsonResponse({"error": "List of NFC UIDs is required"}, status=400)

        user = request.user
        if not user.is_authenticated:
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2 and auth[0].lower() == "basic":
                    try:
                        username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
                        user = authenticate(username=username, password=password)
                    except Exception:
                        pass
        
        product = ProdutItemMaster.objects.get(id=product_id)

        created_bottles = generate_bottles_with_nfc(
            product=product,
            nfc_uids=nfc_uids,
            created_by=user if user and user.is_authenticated else None
        )

        return JsonResponse({
            "message": "Bottles created successfully",
            "count": len(created_bottles),
            "bottles": [
                {
                    "nfc_uid": b.nfc_uid,
                    "serial_number": b.serial_number,
                    "qr_code": b.qr_code
                } 
                for b in created_bottles
            ]
        }, status=201)

    except ProdutItemMaster.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_bottle_details_by_nfc(request):
    try:
        data = json.loads(request.body)
        nfc_uid = data.get("nfc_uid")

        if not nfc_uid:
            return JsonResponse({"error": "NFC UID is required"}, status=400)

        bottle = Bottle.objects.get(nfc_uid=nfc_uid)

        return JsonResponse({
            "id": bottle.id,
            "serial_number": bottle.serial_number,
            "qr_code": bottle.qr_code,
            "status": bottle.status,
            "product_name": bottle.product.product_name if bottle.product else "Unknown",
            "nfc_uid": bottle.nfc_uid,
            "created_at": bottle.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }, status=200)

    except Bottle.DoesNotExist:
        return JsonResponse({"error": "Bottle not found for this NFC"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_van_by_route(request):
    try:
        data = json.loads(request.body)
        route_id = data.get("route_id")
        
        if not route_id:
            return JsonResponse({"error": "Route ID is required"}, status=400)
            
        # Find Van associated with this Route
        from van_management.models import Van_Routes
        
        # Note: routes__route_id assumes RouteMaster has primary key route_id
        # Let's verify RouteMaster PK. It is route_id (UUID).
        van_route = Van_Routes.objects.filter(routes__route_id=route_id).first()
        
        if not van_route or not van_route.van:
            return JsonResponse({"error": "No Van assigned to this Route"}, status=404)
            
        van = van_route.van
        
        return JsonResponse({
            "van_id": str(van.van_id),
            "van_make": van.van_make,
            "plate": van.plate,
            "driver": van.driver.username if van.driver else "No Driver"
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def transfer_bottles_to_van(request):
    try:
        data = json.loads(request.body)
        van_id = data.get("van_id")
        nfc_uids = data.get("nfc_uids", [])
        
        if not van_id:
            return JsonResponse({"error": "Van ID is required"}, status=400)
        
        if not nfc_uids:
             return JsonResponse({"error": "No bottles scanned"}, status=400)
            
        from van_management.models import Van
        try:
            van = Van.objects.get(van_id=van_id)
        except Van.DoesNotExist:
            return JsonResponse({"error": "Van not found"}, status=404)
            
        success_count = 0
        failed_bottles = []
        
        for nfc in nfc_uids:
            try:
                bottle = Bottle.objects.get(nfc_uid=nfc)
                
                # Check if already in this van to avoid redundant logs?
                # But user might want to re-scan to confirm.
                # Let's just update.
                
                old_status = bottle.status
                old_van = bottle.current_van
                
                # Update Bottle Status and Location
                bottle.status = "VAN"
                bottle.current_van = van
                bottle.current_customer = None 
                bottle.save()
                
                # Create Ledger Entry
                BottleLedger.objects.create(
                    bottle=bottle,
                    action="LOAD_TO_VAN",
                    van=van,
                    reference=f"Transfer to {van.van_make} (was {old_status})",
                    created_by="App User"
                )
                success_count += 1
                
            except Bottle.DoesNotExist:
                failed_bottles.append({"nfc": nfc, "reason": "Not found"})
            except Exception as e:
                failed_bottles.append({"nfc": nfc, "reason": str(e)})
                
        return JsonResponse({
            "message": f"Transferred {success_count} bottles",
            "success_count": success_count,
            "failed_count": len(failed_bottles),
            "failed_bottles": failed_bottles
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)