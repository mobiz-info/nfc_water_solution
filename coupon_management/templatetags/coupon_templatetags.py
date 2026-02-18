import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from client_management.models import *
from coupon_management.models import CouponStock
from sales_management.models import *
from van_management.models import VanCouponStock

register = template.Library()

@register.simple_tag
def available_valuable_coupons(coupon_pk):
    return CouponLeaflet.objects.filter(coupon__pk=coupon_pk)

@register.simple_tag
def available_free_coupons(coupon_pk):
    return FreeLeaflet.objects.filter(coupon__pk=coupon_pk)

@register.simple_tag
def get_coupon_designation(pk):
    context = {}
    instance = NewCoupon.objects.get(pk=pk)
    coupon_status = CouponStock.objects.get(couponbook=instance).coupon_stock
    # print(CouponStock.objects.get(couponbook=instance).couponbook.pk)
    
    if coupon_status == "customer":
        customer_instance = CustomerCouponItems.objects.filter(coupon=instance).first()
        # print(customer_instance.coupon)
        # if customer_instance.customer_coupon == None:
        #     customer_instance.delete()
        customer_instance = customer_instance.customer_coupon.customer
        
        context = {
            "pk": customer_instance.pk,
            "name": f"{customer_instance.custom_id} - {customer_instance.customer_name}",
        }
    
    elif coupon_status == "van":
        van_instance = VanCouponStock.objects.filter(coupon=instance)
        if van_instance.exists():
            van_instance = van_instance.latest("created_date").van
        
            context = {
                "pk": van_instance.pk,
                "name": f"{van_instance.plate} - {van_instance.get_van_route()}",
            }
    
    elif coupon_status == "company":
        name = ""
        if instance.branch_id:
            name = instance.branch_id.name
        context = {
            "pk": "",
            "name": name,
        }
        
    elif coupon_status == "used":
        
        context = {
            "pk": "",
            "name": f"Used",
        }
    return context


@register.simple_tag
def redeemed_coupons(supply_id):
    coupon_instances = CustomerSupplyCoupon.objects.filter(customer_supply__pk=supply_id)

    valueable_leafs = []
    free_leafs = []
    coupon_names = set()  # To store distinct coupon names

    for coupon in coupon_instances:
        valueable_leafs.extend(coupon.leaf.all())
        free_leafs.extend(coupon.free_leaf.all())

        # Extract the coupon name (book_num) from the leaflets
        for leaflet in coupon.leaf.all():
            coupon_names.add(leaflet.coupon.book_num)  # Assuming `CouponLeaflet` has `coupon.book_num`
        
        for free_leaflet in coupon.free_leaf.all():
            coupon_names.add(free_leaflet.coupon.book_num)  # Assuming `FreeLeaflet` has `coupon.book_num`

    context = {
        "valueable_leafs": valueable_leafs,
        "free_leafs": free_leafs,
        "coupon_names": list(coupon_names),  # Convert set to list
    }
    return context



