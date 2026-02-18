import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from master.functions import get_next_visit_date
from client_management.models import *
from master.models import *
from van_management.models import *
from van_management.views import find_customers

register = template.Library()

@register.simple_tag
def get_next_visit_day(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
    if not customer.visit_schedule is None:
        next_visit_date = get_next_visit_date(customer.visit_schedule)
        # customer.next_visit_date = next_visit_date
        return next_visit_date
    else:
      return "-"

@register.simple_tag
def bottle_stock(customer_pk):
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

    return supply_qty + custody_qty


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def other_product_rate(customer_pk,product_id):
    rate = ProdutItemMaster.objects.get(pk=product_id).rate
    if (rate_change_instances:=CustomerOtherProductCharges.objects.filter(product_item__pk=product_id,customer__pk=customer_pk)).exists():
        rate = rate_change_instances.first().current_rate
    return rate


@register.simple_tag
def route_bottle_stock():
    route_bottle_counts = {}

    # Fetch all routes
    routes = RouteMaster.objects.all()

    for route in routes:
        total_bottle_count = 0

        # Fetch customers under this route
        customers = Customers.objects.filter(is_guest=False, routes=route)

        for customer in customers:
            custody_count = 0

            # Fetch custody stock if it exists
            custody_stock = CustomerCustodyStock.objects.filter(customer=customer, product__product_name="5 Gallon").first()
            if custody_stock:
                custody_count = custody_stock.quantity 

            # Aggregate supplied bottle count
            total_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).aggregate(
                total_quantity=Sum('quantity')
            )['total_quantity'] or 0

            # Aggregate empty bottles collected
            total_empty_collected = CustomerSupply.objects.filter(customer=customer).aggregate(
                total_quantity=Sum('collected_empty_bottle')
            )['total_quantity'] or 0

            # Calculate total bottle count for the customer
            total_bottle_count += custody_count + total_supplied_count - total_empty_collected

        # Store total count for the route
        route_bottle_counts[route.route_id] = total_bottle_count

    return route_bottle_counts  # Returns a dictionary

@register.simple_tag
def van_bottle_stock():
    """
    Returns a dictionary of {route_id: total_count} for "5 Gallon" bottles.
    """
    try:
        # Get the "5 Gallon" product
        product_5gallon = ProdutItemMaster.objects.get(product_name="5 Gallon")
    except ProdutItemMaster.DoesNotExist:
        return {}

    # Query to get total count of "5 Gallon" bottles per route
    route_stock_data = (
        VanProductItems.objects.filter(product=product_5gallon)
        .values('van_stock__van__van_master__routes__route_id')
        .annotate(total_bottles=Sum('count'))
    )

    # Store results in a dictionary {route_id: total_count}
    route_stock_counts = {
        str(item['van_stock__van__van_master__routes__route_id']): item['total_bottles']
        for item in route_stock_data if item['van_stock__van__van_master__routes__route_id']  # Avoid None keys
    }

    return route_stock_counts


@register.simple_tag
def get_missed_customer_count(request, route_id, date):
    planned_customers = find_customers(request, str(date), route_id) or []
    customer_ids = [
        customer['customer_id'] if not isinstance(customer['customer_id'], dict) else customer['customer_id'].get('id')
        for customer in planned_customers
    ]

    supplied_customers_from_schedule = CustomerSupply.objects.filter(
        customer__pk__in=customer_ids,
        created_date__date=date
    ).count()

    supplied_customers_from_clients = CustomerSupply.objects.filter(
        customer__routes__pk=route_id,
        created_date__date=date
    ).exclude(customer__pk__in=customer_ids).count()

    return {
        'actual_customers': Customers.objects.filter(is_guest=False, routes__pk=route_id, is_active=True).count(),
        'planned_visitors': len(planned_customers),
        'missed_customers': len(planned_customers) - supplied_customers_from_schedule,
        'supplied_customers_from_schedule': supplied_customers_from_schedule,
        'supplied_customers_from_clients': supplied_customers_from_clients,
    }
