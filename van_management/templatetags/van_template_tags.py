from datetime import datetime, timedelta
from decimal import Decimal

from django import template
from django.db.models import Q, Sum,Subquery,Value
from django.db.models.functions import Coalesce

from accounts.models import CustomUser
from client_management.models import CustodyCustomItems, CustomerReturnItems, CustomerSupply, CustomerSupplyItems, OutstandingAmount, OutstandingCoupon, OutstandingProduct
from master.models import CategoryMaster
from product.models import Staff_IssueOrders, Staff_Orders_details,ProdutItemMaster
from sales_management.models import CollectionPayment
from van_management.models import AuditDetails, CustomerProductReturn, Offload, OffloadRequestItems, Van, Van_Routes, VanCouponStock, VanProductItems, VanProductStock,FreelanceVehicleOtherProductCharges, VanSaleDamage
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round

register = template.Library()

@register.simple_tag
def get_empty_bottles(salesman):
    try:
        return CustomerSupply.objects.filter(salesman=salesman,created_date__date=datetime.today().date()).aggregate(total=Coalesce(Sum('collected_empty_bottle'), Value(0)))['total']
    except CustomerSupply.DoesNotExist:
        return 0
    
@register.simple_tag
def get_van_product_wise_stock(date, van, product):

    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        date = datetime.today().date()
    print("van")
    print(van)
    print("product")
    print(product)
    van = Van.objects.get(pk=van)
    product = ProdutItemMaster.objects.get(pk=product)

    # -------- OPENING --------
    opening = 0

    yesterday = date - timedelta(days=1)

    prev_vps = VanProductStock.objects.filter(
        created_date=yesterday,
        van=van,
        product=product
    ).first()
    vps = VanProductStock.objects.filter(
        created_date=date,
        van=van,
        product=product
    ).first()

    opening = prev_vps.closing_count if prev_vps else 0
    empty_bottle = vps.empty_can_count if vps else 0

    # -------- ISSUED --------
    issued = Staff_IssueOrders.objects.filter(
        van=van,
        product_id=product,
        staff_Orders_details_id__staff_order_id__order_date=date
    ).aggregate(qty=Sum("quantity_issued"))["qty"] or 0

    # -------- SOLD --------
    sold = CustomerSupplyItems.objects.filter(
        product=product,
        customer_supply__salesman=van.salesman,
        customer_supply__created_date__date=date
    ).aggregate(qty=Sum("quantity"))["qty"] or 0

    # -------- FOC --------
    foc = CustomerSupply.objects.filter(
        salesman=van.salesman,
        created_date__date=date
    ).aggregate(qty=Sum("allocate_bottle_to_free"))["qty"] or 0

    # -------- RETURN --------
    returned = CustomerProductReturn.objects.filter(
        product=product,
        van=van,
        created_date__date=date
    ).aggregate(qty=Sum("quantity"))["qty"] or 0

    # -------- DAMAGE --------
    damage = VanSaleDamage.objects.filter(
        van=van,
        product=product,
        created_date__date=date
    ).aggregate(qty=Sum("quantity"))["qty"] or 0

    # -------- OFFLOAD --------
    offload = OffloadRequestItems.objects.filter(
        offload_request__van=van,
        offload_request__date=date,
        offload_request__status=True,
        product=product
    ).aggregate(qty=Sum("quantity"))["qty"] or 0

    # -------- CUSTODY --------
    custody = CustodyCustomItems.objects.filter(
        product=product,
        custody_custom__created_date__date=date
    ).aggregate(qty=Sum("quantity"))["qty"] or 0

    custody_pullout = CustomerReturnItems.objects.filter(
        customer_return__created_date__date=date,
        product=product
    ).aggregate(qty=Sum('quantity'))['qty'] or 0

    # -------- NET LOAD --------
    net_load = opening + issued

    # -------- CLOSING --------
    closing = (
        opening
        + issued
        - sold
        - foc
        + returned
        + custody_pullout
        - damage
        - offload
        - custody
    )

    return {
        "opening_stock": int(opening),
        "issued_count": int(issued),
        "net_load": int(net_load),
        "sold_count": int(sold),
        "foc_count": int(foc),
        "return_count": int(returned),
        "damage_count": int(damage),
        "offload_count": int(offload),
        "custody_count": int(custody),
        "empty_bottle": int(empty_bottle),
        "custody_pullout": int(custody_pullout),
        "closing_count": int(max(closing, 0)),
    }

    
@register.simple_tag
def get_five_gallon_ratewise_count(rate, date, routename, salesman_id=None):
    qs = CustomerSupplyItems.objects.filter(
        customer_supply__supply_date__date=date,
        product__product_name="5 Gallon",
        customer_supply__customer__routes__route_name=routename,
        quantity__gt=0,
        amount__gt=0
    )

    if salesman_id:
        qs = qs.filter(customer_supply__salesman_id=salesman_id)

    qs = qs.annotate(
        calculated_rate=Round(
            ExpressionWrapper(
                F("amount") / F("quantity"),
                output_field=DecimalField(max_digits=10, decimal_places=6)
            ),
            2
        )
    ).filter(
        calculated_rate=rate  # ✅ match derived rate
    )

    return {
        "debit_amount_count": (
            qs.filter(customer_supply__amount_recieved__gt=0)
              .aggregate(total=Sum("quantity"))["total"] or 0
        ),
        "credit_amount_count": (
            qs.filter(customer_supply__amount_recieved=0)
              .exclude(customer_supply__customer__sales_type__in=["FOC", "CASH COUPON"])
              .aggregate(total=Sum("quantity"))["total"] or 0
        ),
        "coupon_amount_count": (
            qs.filter(customer_supply__customer__sales_type="CASH COUPON")
              .aggregate(total=Sum("quantity"))["total"] or 0
        ),
    }
    
@register.simple_tag
def get_coupon_vanstock_count(van_pk,date,coupon_type):
    return VanCouponStock.objects.filter(created_date=date,van__pk=van_pk,coupon__coupon_type__coupon_type_name=coupon_type).aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    

@register.simple_tag
def get_van_coupon_wise_stock(date, van, coupon):
    if VanCouponStock.objects.filter(created_date=date, van=van, coupon__pk=coupon).exists():
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()

        van = Van.objects.get(pk=van)
        van_stock = VanCouponStock.objects.get(created_date=date, van=van, coupon__pk=coupon)

        staff_order_details = Staff_Orders_details.objects.filter(
            staff_order_id__created_date__date=date,
            product_id__pk=coupon,
            staff_order_id__created_by=van.salesman.pk
        )
        issued_count = staff_order_details.aggregate(total_count=Sum('issued_qty'))['total_count'] or 0

        total_stock = van_stock.stock + van_stock.opening_count
        sold_count = van_stock.sold_count
        offload_count = Offload.objects.filter(
            van=van,
            product__pk=coupon,
            created_date__date=date
        ).aggregate(total_count=Sum('quantity'))['total_count'] or 0

        return {
            "opening_stock": van_stock.opening_count,
            "requested_count": Staff_Orders_details.objects.filter(
                product_id__pk=coupon,
                staff_order_id__created_date__date=date,
                created_by=van.salesman.pk
            ).aggregate(total_count=Sum('count'))['total_count'] or 0,
            "issued_count": issued_count,
            "return_count": van_stock.return_count,
            "sold_count": sold_count,
            "closing_count": van_stock.closing_count,
            "offload_count": offload_count,
            "change_count": van_stock.change_count,
            "damage_count": van_stock.damage_count,
            "total_stock": total_stock
        }
    return {}


@register.simple_tag
def other_product_rate(van_pk,product_id):
    rate = ProdutItemMaster.objects.get(pk=product_id).rate
    if (rate_change_instances:=FreelanceVehicleOtherProductCharges.objects.filter(product_item__pk=product_id,van__pk=van_pk)).exists():
        rate = rate_change_instances.first().current_rate
    return rate


@register.simple_tag
def get_audit_details(audit_detail_id):
    audit_detail_instance = AuditDetails.objects.get(pk=audit_detail_id)

    # Ensure Decimal safety
    current_amount = OutstandingAmount.objects.filter(
        customer_outstanding__customer__pk=audit_detail_instance.customer.pk,
        customer_outstanding__created_date__date__lte=audit_detail_instance.audit_base.start_date.date()
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal("0.00")

    collection_amount = CollectionPayment.objects.filter(
        customer__pk=audit_detail_instance.customer.pk,
        created_date__date__lte=audit_detail_instance.audit_base.start_date.date()
    ).aggregate(total_amount_received=Sum('amount_received'))['total_amount_received'] or Decimal("0.00")

    customer_current_outstanding_amount = current_amount - collection_amount

    customer_current_outstanding_bottle = OutstandingProduct.objects.filter(
        customer_outstanding__customer__pk=audit_detail_instance.customer.pk,
        customer_outstanding__created_date__date__lte=audit_detail_instance.audit_base.start_date.date()
    ).aggregate(total_bottles=Sum('empty_bottle'))['total_bottles'] or 0

    customer_current_outstanding_coupon = OutstandingCoupon.objects.filter(
        customer_outstanding__customer__pk=audit_detail_instance.customer.pk,
        customer_outstanding__created_date__date__lte=audit_detail_instance.audit_base.start_date.date()
    ).aggregate(total_coupons=Sum('count'))['total_coupons'] or 0

    # Guard against None
    outstanding_amount = audit_detail_instance.outstanding_amount or Decimal("0.00")
    outstanding_coupon = audit_detail_instance.outstanding_coupon or 0
    outstanding_bottle = audit_detail_instance.bottle_outstanding or 0

    response = {
        "customer_current_outstanding_amount": customer_current_outstanding_amount,
        "amount_variation": customer_current_outstanding_amount - outstanding_amount,

        "customer_current_outstanding_coupon": customer_current_outstanding_coupon,
        "coupon_variation": customer_current_outstanding_coupon - outstanding_coupon,

        "customer_current_outstanding_bottle": customer_current_outstanding_bottle,
        "bottle_variation": customer_current_outstanding_bottle - outstanding_bottle,
    }
    return response