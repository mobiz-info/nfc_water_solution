import datetime
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.db.models import Sum

from accounts.models import Customers
from client_management.models import CustodyCustomItems, CustomerCustodyStock
from master.models import RouteMaster
from product.models import ProdutItemMaster
from django.db.models import Sum, Q

def custody_product_summary(request):
    """
    Page 1: Product-wise custody summary (Deposit + Non-deposit combined)
    """

    products = (
        CustodyCustomItems.objects
        .filter(product__isnull=False)
        .exclude(product__category__category_name__icontains="coupon")
        .values(
            "product",                       # product UUID
            "product__product_name"          # product name
        )
        .annotate(
            total_qty=Sum("quantity")
        )
        .order_by("product__product_name")
    )

    context = {
        "products": products
    }

    return render(
        request,
        "client_management/custody/product_summary.html",
        context
    )


def custody_route_summary(request, product_id):
    """
    Page 2: Route-wise custody summary (Deposit + Non-deposit combined)
    """

    product = get_object_or_404(ProdutItemMaster, pk=product_id)

    routes = (
        CustodyCustomItems.objects
        .filter(
            product=product,
            custody_custom__customer__routes__isnull=False
        )
        .exclude(product__category__category_name__icontains="coupon")
        .values(
            "custody_custom__customer__routes__route_id",
            "custody_custom__customer__routes__route_name",
        )
        .annotate(
            total_qty=Sum("quantity")
        )
        .order_by(
            "custody_custom__customer__routes__route_name"
        )
    )

    print("routes",routes)

    context = {
        "product": product,
        "routes": routes,
    }

    return render(
        request,
        "client_management/custody/route_summary.html",
        context
    )


def custody_customer_summary(request, product_id, route_id):
    """
    Page 3: Customer-wise custody summary with search
    """

    product = get_object_or_404(ProdutItemMaster, pk=product_id)
    route = get_object_or_404(RouteMaster, pk=route_id)

    search = request.GET.get("search", "").strip()

    customers_qs = (
        CustodyCustomItems.objects
        .filter(
            product=product,
            custody_custom__customer__routes=route
        )
        .exclude(
            product__category__category_name__icontains="coupon"
        )
    )

    
    if search:
        customers_qs = customers_qs.filter(
            Q(custody_custom__customer__customer_name__icontains=search) |
            Q(custody_custom__customer__custom_id__icontains=search)
        )

    customers = (
        customers_qs
        .values(
            "custody_custom__customer__customer_id",
            "custody_custom__customer__customer_name",
            "custody_custom__customer__custom_id",
        )
        .annotate(
            total_qty=Sum("quantity")
        )
        .order_by(
            "custody_custom__customer__customer_name"
        )
    )

    context = {
        "product": product,
        "route": route,
        "customers": customers,
        "search": search,  
    }

    return render(
        request,
        "client_management/custody/customer_summary.html",
        context
    )

def custody_ledger(request, product_id, route_id, customer_id):
    """
    Page 4: Customer Custody Ledger (Date-wise)
    """

    product = get_object_or_404(ProdutItemMaster, pk=product_id)
    route = get_object_or_404(RouteMaster, pk=route_id)
    customer = get_object_or_404(Customers, pk=customer_id)

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # ✅ BASE QUERY (LEDGER SOURCE)
    ledger_qs = CustodyCustomItems.objects.filter(
        product_id=product_id,
        custody_custom__customer_id=customer_id,
        custody_custom__customer__routes_id=route_id
    ).select_related(
        "custody_custom",
        "custody_custom__customer"
    )

    # ✅ DATE FILTER (FROM HEADER MODEL)
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        ledger_qs = ledger_qs.filter(
            custody_custom__created_date__date__gte=start_date
        )

    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        ledger_qs = ledger_qs.filter(
            custody_custom__created_date__date__lte=end_date
        )

    ledger_qs = ledger_qs.order_by("custody_custom__created_date")

    # ✅ RUNNING BALANCE
    running_qty = 0
    rows = []

    for item in ledger_qs:
        running_qty += item.quantity

        rows.append({
            "created_date": item.custody_custom.created_date,
            "qty": item.quantity,
            "deposit_type": item.custody_custom.deposit_type,
            "amount": item.amount,
            "can_deposite_chrge": item.can_deposite_chrge,
            "five_gallon_water_charge": item.five_gallon_water_charge,
            "running_qty": running_qty,
        })

    context = {
        "product": product,
        "route": route,
        "customer": customer,
        "rows": rows,
        "total_qty": running_qty,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(
        request,
        "client_management/custody/custody_ledger.html",
        context
    )


def customer_wise_custody_summary(request):
    

    product_id = request.GET.get("product")
    route_id = request.GET.get("route")
    search = request.GET.get("search", "").strip()

    products = ProdutItemMaster.objects.exclude(
    category__category_name__icontains="coupon"
    )
    routes = RouteMaster.objects.all()
    customers = []
    if product_id and route_id:

        customers_qs = CustodyCustomItems.objects.exclude(
            product__category__category_name__icontains="coupon"
        ).filter(
            product_id=product_id,
            custody_custom__customer__routes_id=route_id
        )

        if search:
            customers_qs = customers_qs.filter(
                Q(custody_custom__customer__customer_name__icontains=search) |
                Q(custody_custom__customer__custom_id__icontains=search)
            )

        customers = (
            customers_qs
            .values(
                "custody_custom__customer__customer_id",
                "custody_custom__customer__customer_name",
                "custody_custom__customer__custom_id",
            )
            .annotate(
                total_qty=Sum("quantity")
            )
            .order_by(
                "custody_custom__customer__customer_name"
            )
        )

    context = {
        "customers": customers,
        "products": products,
        "routes": routes,
        "selected_product": product_id,
        "selected_route": route_id,
        "search": search,
    }

    return render(
        request,
        "client_management/custody/customer_wise_custody_summary.html",
        context
    )