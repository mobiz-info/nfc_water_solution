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

# def get_last_number(prefix):
#     # Regex to match ANY date pattern with the prefix and a number
#     # Matches: dd-mm-PREFIX123
#     regex = rf"^\d{{2}}-\d{{2}}-{prefix}(\d+)$"
    
#     # Fetch all matching serial numbers regardless of date
#     serials = Bottle.objects.filter(serial_number__regex=regex).values_list('serial_number', flat=True)
    
#     max_number = 0
    
#     for serial in serials:
#         match = re.search(r"(\d+)$", serial)
#         if match:
#             number = int(match.group(1))
#             if number > max_number:
#                 max_number = number
                
#     return max_number

def get_last_number(prefix):
    # Match pattern like A1-03/26
    regex = rf"^{prefix}(\d+)-\d{{2}}/\d{{2}}$"

    serials = Bottle.objects.filter(
        serial_number__regex=regex
    ).values_list("serial_number", flat=True)

    max_number = 0

    for serial in serials:
        match = re.search(rf"{prefix}(\d+)", serial)
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

    last_number = get_last_number(prefix)

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
                reference=f"Initial Stock ({date_str})"
            )
        )

    BottleLedger.objects.bulk_create(ledgers)

    return bottles


# @csrf_exempt
# def preview_bottles(request):
#     data = json.loads(request.body)
#     qty = int(data["qty"])
#     prefix = data.get("prefix", "BTL")

#     today = datetime.now().strftime("%d-%m")
#     last_no = get_last_number(prefix)

#     serials = [
#         f"{today}-{prefix}{last_no + i}"
#         for i in range(1, qty + 1)
#     ]

#     return JsonResponse({"serials": serials})
@csrf_exempt
def preview_bottles(request):
    data = json.loads(request.body)
    qty = int(data["qty"])
    prefix = data.get("prefix", "A")

    today = datetime.now().strftime("%m/%y")   # 03/26
    last_no = get_last_number(prefix)

    serials = [
        f"{prefix}{last_no + i}-{today}"
        for i in range(1, qty + 1)
    ]

    return JsonResponse({"serials": serials})

@csrf_exempt
def refill_bottles(request):
    try:
        data = json.loads(request.body)
        nfc_uids = data.get("nfc_uids", [])
        
        if not nfc_uids:
             return JsonResponse({"error": "No bottles scanned"}, status=400)
             
        success_count = 0
        failed_bottles = []
        
        for nfc in nfc_uids:
            try:
                bottle = Bottle.objects.get(nfc_uid=nfc)
                bottle.is_filled = True
                if bottle.visited_customer_in_current_cycle:
                    bottle.bottle_cycle += 1
                    bottle.visited_customer_in_current_cycle = False
                bottle.save()
                
                BottleLedger.objects.create(
                    bottle=bottle,
                    action="REFILL",
                    reference="Refilled at Plant",
                    created_by="App User" # Or authenticated user
                )
                success_count += 1
            except Bottle.DoesNotExist:
                failed_bottles.append({"nfc": nfc, "reason": "Not found"})
            except Exception as e:
                failed_bottles.append({"nfc": nfc, "reason": str(e)})
                
        return JsonResponse({
            "message": f"Refilled {success_count} bottles",
            "success_count": success_count,
            "failed_count": len(failed_bottles),
            "failed_bottles": failed_bottles
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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
    prefix="A",
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
    date_str = today.strftime("%m/%y")

    last_number = get_last_number(prefix)

    bottles = []
    ledgers = []

    for i, nfc_uid in enumerate(nfc_uids):
        serial = f"{prefix}{last_number + i + 1}-{date_str}"

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
                reference=f"Initial NFC Stock ({date_str})",
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
            "created_at": bottle.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_filled": bottle.is_filled,
            "current_van": {
                "id": bottle.current_van.van_id,
                "name": bottle.current_van.get_van_route()
             } if bottle.current_van else None,
            "current_customer": {
                "id": bottle.current_customer.customer_id,
                "name": bottle.current_customer.customer_name
            } if bottle.current_customer else None
        }, status=200)

    except Bottle.DoesNotExist:
        return JsonResponse({"error": "Bottle not found for this NFC"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_bottle_by_qr(request):
    """Look up a bottle by its QR code value. Returns the same structure as get_bottle_details_by_nfc."""
    try:
        data = json.loads(request.body)
        qr_code = data.get("qr_code")

        if not qr_code:
            return JsonResponse({"error": "QR code is required"}, status=400)

        bottle = Bottle.objects.get(qr_code=qr_code)

        return JsonResponse({
            "id": bottle.id,
            "serial_number": bottle.serial_number,
            "qr_code": bottle.qr_code,
            "nfc_uid": bottle.nfc_uid,
            "status": bottle.status,
            "product_name": bottle.product.product_name if bottle.product else "Unknown",
            "created_at": bottle.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_filled": bottle.is_filled,
            "current_van": {
                "id": bottle.current_van.van_id,
                "name": bottle.current_van.get_van_route()
            } if bottle.current_van else None,
            "current_customer": {
                "id": bottle.current_customer.customer_id,
                "name": bottle.current_customer.customer_name
            } if bottle.current_customer else None,
        }, status=200)

    except Bottle.DoesNotExist:
        return JsonResponse({"error": "Bottle not found for this QR code"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



from django.contrib.auth.decorators import login_required

@login_required
def bottle_stock_report(request):
    """
    Report showing Opening, In, Out, Closing stock for a selected Date and Route.
    """
    from datetime import datetime, timedelta
    from django.db.models import Sum, Case, When, IntegerField, F
    from master.models import RouteMaster
    
    routes = RouteMaster.objects.all()
    selected_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_route_id = request.GET.get('route')
    selected_status = request.GET.get('status')
    
    context = {
        'routes': routes,
        'selected_date': selected_date,
        'selected_route_id': selected_route_id,
        'selected_status': selected_status,
        'report_data': None
    }

    if selected_route_id and selected_date:
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            route = RouteMaster.objects.get(route_id=selected_route_id)
            
            ledger_qs = BottleLedger.objects.filter(route=route)
            
            if selected_status:
                if selected_status == "FRESH":
                    ledger_qs = ledger_qs.filter(bottle__is_filled=True)

                elif selected_status == "USED":
                    ledger_qs = ledger_qs.filter(bottle__is_filled=False)

                elif selected_status == "DAMAGED":
                    ledger_qs = ledger_qs.filter(action="DAMAGE")

                elif selected_status == "SERVICE":
                    ledger_qs = ledger_qs.filter(action="REFILL")

                elif selected_status == "TRANSFER":
                    ledger_qs = ledger_qs.filter(action="LOAD_TO_VAN")
            
            # OPENING
            opening_qs = ledger_qs.filter(created_at__date__lt=target_date)
            
            opening_plus = opening_qs.filter(action__in=["LOAD_TO_VAN", "RETURN"]).count()
            opening_minus = opening_qs.filter(action__in=["SUPPLY", "OFFLOAD"]).count()
            opening_stock = opening_plus - opening_minus
            
            # TODAY IN/OUT
            today_qs = ledger_qs.filter(created_at__date=target_date)
            
            today_in = today_qs.filter(action__in=["LOAD_TO_VAN", "RETURN"]).count()
            today_out = today_qs.filter(action__in=["SUPPLY", "OFFLOAD"]).count()
            
            closing_stock = opening_stock + today_in - today_out
            
            context['report_data'] = {
                'opening_stock': opening_stock,
                'in_stock': today_in,
                'out_stock': today_out,
                'closing_stock': closing_stock,
            }

        except Exception as e:
            print(e)
            
    return render(request, 'bottle_management/bottle_stock_report.html', context)

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
        route_id = data.get("route_id")
        
        if not van_id:
            return JsonResponse({"error": "Van ID is required"}, status=400)
        
        if not nfc_uids:
             return JsonResponse({"error": "No bottles scanned"}, status=400)
            
        from van_management.models import Van
        from master.models import RouteMaster

        try:
            van = Van.objects.get(van_id=van_id)
        except Van.DoesNotExist:
            return JsonResponse({"error": "Van not found"}, status=404)
            
        # Resolved Route
        route_obj = None
        if route_id:
            try:
                route_obj = RouteMaster.objects.get(route_id=route_id)
            except RouteMaster.DoesNotExist:
                pass
        
        if not route_obj:
            route_obj = van.get_van_route_obj()
            
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
                    created_by="App User",
                    route=route_obj
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


def periodic_bottle_movement_report(request):
    try:
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        action = request.GET.get('action')

        movements = BottleLedger.objects.all().order_by('-created_at')

        if from_date:
            movements = movements.filter(created_at__date__gte=from_date)
        
        if to_date:
            movements = movements.filter(created_at__date__lte=to_date)

        if action:
            movements = movements.filter(action=action)

        context = {
            'movements': movements,
            'from_date': from_date,
            'to_date': to_date,
            'selected_action': action,
            'action_choices': BottleLedger.ACTION_CHOICES,
        }
        return render(request, 'bottle_management/movement_report.html', context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def bottle_cycle_report(request):
    try:
        q = request.GET.get('q', '').strip()
        bottle = None
        movements = None

        if q:
            # Search by serial number or nfc_uid
            from django.db.models import Q
            bottle = Bottle.objects.filter(Q(serial_number=q) | Q(nfc_uid=q)).first()
            if bottle:
                movements = BottleLedger.objects.filter(bottle=bottle).order_by('-created_at')

        context = {
            'q': q,
            'bottle': bottle,
            'movements': movements,
        }
        return render(request, 'bottle_management/bottle_cycle_report.html', context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def bottles_report(request):
    """
    Report listing all bottles with their details:
    Created Date, Current Status, Bottle Cycle, Route, QR Code (server-side generated).
    Supports filtering by status and searching by serial number / QR code.
    """
    import qrcode
    import io
    import base64
    from django.db.models import Q

    status_filter = request.GET.get('status', '').strip()
    search_q = request.GET.get('q', '').strip()

    qs = Bottle.objects.filter(is_deleted=False).select_related('product', 'current_van', 'current_customer', 'current_route').order_by('-created_at')

    if status_filter:
        qs = qs.filter(status=status_filter)

    if search_q:
        qs = qs.filter(
            Q(serial_number__icontains=search_q) | Q(qr_code__icontains=search_q)
        )

    def make_qr_b64(text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=2,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    bottles_data = []
    for bottle in qs:
        bottles_data.append({
            'bottle': bottle,
            'qr_b64': make_qr_b64(bottle.serial_number),
        })

    context = {
        'bottles_data': bottles_data,
        'status_choices': Bottle.STATUS_CHOICES,
        'selected_status': status_filter,
        'search_q': search_q,
        'total_count': qs.count(),
    }
    return render(request, 'bottle_management/bottles_report.html', context)


@login_required
def bottle_delete(request, pk):

    try:
        bottle = Bottle.objects.get(pk=pk, is_deleted=False)

        bottle.is_deleted = True
        bottle.save()

        return JsonResponse({
            "status": "success",
            "message": "Bottle deleted successfully"
        })

    except Bottle.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Bottle not found"
        })
        
        
@login_required
def bottle_stock_transfer_summary(request):

    from datetime import datetime
    from master.models import RouteMaster

    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    report_type = request.GET.get("report_type", "summary")

    summary_rows = []
    route_rows = []

    if from_date_str and to_date_str:

        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

        ledger = BottleLedger.objects.all()

        # SUMMARY REPORT
        if report_type == "summary":

            types = [
                ("Fresh", {"bottle__is_filled": True}),
                ("Used", {"bottle__is_filled": False}),
                ("Service", {"action": "SERVICE"}),
                ("Scrap", {"action": "DAMAGE"}),
            ]

            for label, condition in types:

                qs = ledger.filter(**condition)

                opening_qs = qs.filter(created_at__date__lt=from_date)

                opening_plus = opening_qs.filter(
                    action__in=["LOAD_TO_VAN", "RETURN"]
                ).count()

                opening_minus = opening_qs.filter(
                    action__in=["SUPPLY", "OFFLOAD"]
                ).count()

                opening = opening_plus - opening_minus

                period_qs = qs.filter(
                    created_at__date__range=[from_date, to_date]
                )

                in_count = period_qs.filter(
                    action__in=["LOAD_TO_VAN", "RETURN"]
                ).count()

                out_count = period_qs.filter(
                    action__in=["SUPPLY", "OFFLOAD"]
                ).count()

                closing = opening + in_count - out_count

                summary_rows.append({
                    "type": label,
                    "opening": opening,
                    "in": in_count,
                    "out": out_count,
                    "closing": closing
                })

        # ROUTE REPORT
        else:

            routes = RouteMaster.objects.all()

            for route in routes:

                qs = ledger.filter(route=route)

                opening_plus = qs.filter(
                    created_at__date__lt=from_date,
                    action__in=["LOAD_TO_VAN", "RETURN"]
                ).count()

                opening_minus = qs.filter(
                    created_at__date__lt=from_date,
                    action__in=["SUPPLY", "OFFLOAD"]
                ).count()

                opening = opening_plus - opening_minus

                period_qs = qs.filter(
                    created_at__date__range=[from_date, to_date]
                )

                issued = period_qs.filter(
                    action__in=["SUPPLY", "FOC"]
                ).count()

                removed = period_qs.filter(
                    action__in=["SERVICE", "DAMAGE"]
                ).count()

                closing = opening + issued - removed

                route_rows.append({
                    "route": route.route_name,
                    "opening": opening,
                    "issued": issued,
                    "removed": removed,
                    "closing": closing
                })

    context = {
        "report_type": report_type,
        "from_date": from_date_str,   # keep string
        "to_date": to_date_str,       # keep string
        "summary_rows": summary_rows,
        "route_rows": route_rows
    }

    return render(
        request,
        "bottle_management/bottle_stock_transfer_summary.html",
        context
    )