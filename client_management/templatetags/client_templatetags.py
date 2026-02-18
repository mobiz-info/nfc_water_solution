import datetime
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from django import template
from django.db.models import Q, Sum, F, Case, When, IntegerField

from accounts.models import Customers
from apiservices.serializers import CouponLeafSerializer, FreeLeafletSerializer
from client_management.models import *
from sales_management.models import *

register = template.Library()

@register.simple_tag
def route_wise_bottle_count(route_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__routes__pk=route_pk, product__product_name="5 Gallon")
    
    bottle_supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    bottle_to_custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    bottle_to_paid = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_paid'))['total_quantity'] or 0
    
    foc_supply = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_free'))['total_quantity'] or 0
    empty_bottle_collected = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__collected_empty_bottle'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__routes__pk=route_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__routes__pk=route_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(((bottle_supplied - bottle_to_custody - bottle_to_paid) + foc_supply) - empty_bottle_collected)
    custody_qty = abs(custody_quantity - custody_return)
    
    return supply_qty + custody_qty


@register.simple_tag
def route_wise_customer_bottle_count(customer_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__pk=customer_pk, product__product_name="5 Gallon")
    
    bottle_supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    bottle_to_custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    bottle_to_paid = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_paid'))['total_quantity'] or 0
    
    foc_supply = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_free'))['total_quantity'] or 0
    empty_bottle_collected = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__collected_empty_bottle'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(((bottle_supplied - bottle_to_custody - bottle_to_paid) + foc_supply) - empty_bottle_collected)
    custody_qty = abs(custody_quantity - custody_return)
    
    return {
        'supply_qty': supply_qty,
        'custody_qty': custody_qty,
        'total_bottle_count': supply_qty + custody_qty,
    }
        
        
@register.simple_tag
def get_outstanding_amount(customer_id, date, salesman_id=None):
    if not customer_id:
        return Decimal("0.00")

    # -------------------- OUTSTANDING --------------------
    outstanding_qs = OutstandingAmount.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__date__lte=date
    )

    if salesman_id:
            outstanding_qs = outstanding_qs.filter(
                customer_outstanding__created_by=salesman_id
            )

    outstanding_amount = outstanding_qs.aggregate(
        total=Sum('amount')
    )['total'] or Decimal("0.00")

    # -------------------- COLLECTION --------------------
    collection_qs = CollectionPayment.objects.filter(
        customer__pk=customer_id,
        created_date__date__lte=date
    )

    if salesman_id:
        collection_qs = collection_qs.filter(salesman_id=salesman_id)

    collection_amount = collection_qs.aggregate(
        total=Sum('amount_received')
    )['total'] or Decimal("0.00")

    # -------------------- NET --------------------
    return outstanding_amount - collection_amount
    # if outstanding_amounts > collection_amount:
    # else:
    #     return collection_amount - outstanding_amounts

@register.simple_tag
def get_outstanding_bottles(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_bottles = OutstandingProduct.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date
    ).aggregate(total_bottles=Sum('empty_bottle'))['total_bottles'] or 0
    return outstanding_bottles

@register.simple_tag
def get_outstanding_coupons(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_coupons = OutstandingCoupon.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date,
    ).aggregate(total_coupons=Sum('count'))
    
    return outstanding_coupons.get('total_coupons') or 0


@register.simple_tag
def get_customer_coupon_leafs(customer_id):
    leafs = {}
    coupon_ids_queryset = CustomerCouponItems.objects.filter(customer_coupon__customer_id=customer_id).values_list('coupon__pk', flat=True)
    
    coupon_leafs = CouponLeaflet.objects.filter(used=False,coupon__pk__in=list(coupon_ids_queryset)).order_by("leaflet_name")
    coupon_leafs_data = CouponLeafSerializer(coupon_leafs, many=True).data
    
    free_leafs = FreeLeaflet.objects.filter(used=False,coupon__pk__in=list(coupon_ids_queryset)).order_by("leaflet_name")
    free_leafs_data = FreeLeafletSerializer(free_leafs, many=True).data
    
    leafs = coupon_leafs_data + free_leafs_data
    return leafs

@register.simple_tag
def get_customer_outstanding_aging(route=None):
    if not route:
        return []

    aging_report = []
    current_date = datetime.now().date()

    # Step 1: Get outstanding amounts for customers in the given route
    outstanding_data = OutstandingAmount.objects.filter(
        customer_outstanding__customer__routes__route_name=route
    ).values(
        'customer_outstanding__customer__customer_id',
        'customer_outstanding__customer__customer_name'
    ).annotate(
        total_outstanding=Sum('amount'),
        less_than_30=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gt=current_date - timezone.timedelta(days=30),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_31_and_60=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gt=current_date - timezone.timedelta(days=60),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=30),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_61_and_90=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gt=current_date - timezone.timedelta(days=90),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=60),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_91_and_150=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gt=current_date - timezone.timedelta(days=150),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=90),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_151_and_365=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gt=current_date - timezone.timedelta(days=365),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=150),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        more_than_365=Sum(
            Case(
                When(
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=365),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        )
    )

    # Step 2: For each customer, calculate total collections and subtract from outstanding
    for data in outstanding_data:
        customer_id = data['customer_outstanding__customer__customer_id']

        # Calculate collections for each bucket
        collected = {
            'less_than_30': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__gt=current_date - timezone.timedelta(days=30),
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
            'between_31_and_60': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__gt=current_date - timezone.timedelta(days=60),
                created_date__date__lt=current_date - timezone.timedelta(days=30)
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
            'between_61_and_90': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__gt=current_date - timezone.timedelta(days=90),
                created_date__date__lt=current_date - timezone.timedelta(days=60)
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
            'between_91_and_150': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__gt=current_date - timezone.timedelta(days=150),
                created_date__date__lt=current_date - timezone.timedelta(days=90)
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
            'between_151_and_365': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__gt=current_date - timezone.timedelta(days=365),
                created_date__date__lt=current_date - timezone.timedelta(days=150)
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
            'more_than_365': CollectionPayment.objects.filter(
                customer__customer_id=customer_id,
                created_date__date__lt=current_date - timezone.timedelta(days=365)
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0,
        }

        # Prepare aging data
        aging_data = {
            'customer_id': customer_id,
            'customer_name': data['customer_outstanding__customer__customer_name'],
            'less_than_30': data['less_than_30'] - collected['less_than_30'],
            'between_31_and_60': data['between_31_and_60'] - collected['between_31_and_60'],
            'between_61_and_90': data['between_61_and_90'] - collected['between_61_and_90'],
            'between_91_and_150': data['between_91_and_150'] - collected['between_91_and_150'],
            'between_151_and_365': data['between_151_and_365'] - collected['between_151_and_365'],
            'more_than_365': data['more_than_365'] - collected['more_than_365'],
        }

        # Calculate grand total
        aging_data['grand_total'] = sum(
            value for key, value in aging_data.items()
            if key not in {'customer_id', 'customer_name'}
        )

        if aging_data['grand_total'] > 0:
            aging_report.append(aging_data)

    return aging_report


@register.simple_tag
def get_customer_wise_outstanding_details(customer, closing_date, to_date):
    
    opening_amount = OutstandingAmount.objects.filter(customer_outstanding__customer__pk=customer, customer_outstanding__created_date__date__lte=closing_date).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    opening_collection = CollectionPayment.objects.filter(customer__pk=customer, created_date__date__lte=closing_date).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    
    opening_amount = opening_amount - opening_collection
    
    collection_upto = CollectionPayment.objects.filter(customer__pk=customer, created_date__date__gt=closing_date, created_date__date__lt=to_date).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    
    return{
        "opening_amount": opening_amount,
        "collection_upto": collection_upto,
        "balance_amount": opening_amount - collection_upto,
    }