import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import CustomUser
from master.models import CategoryMaster
from product.models import ProdutItemMaster
from van_management.models import Van_Routes, VanCouponStock, VanProductStock

register = template.Library()

@register.simple_tag
def get_salesman_name(staff_id):
    try:
        # Ensure to sanitize and validate staff_id if needed
        salesman = CustomUser.objects.get(id=staff_id)
        return salesman.get_full_name()
    except CustomUser.DoesNotExist:
        return "--"
    
@register.simple_tag
def get_route_name(staff_id):
    try:
        return Van_Routes.objects.get(van__salesman__pk=staff_id)
    except :
        return "--"
    
@register.simple_tag
def get_categories():
    try:
        return CategoryMaster.objects.all()
    except :
        return "--"
    
@register.simple_tag
def get_van_current_stock(van,product):
    try :
        product = ProdutItemMaster.objects.get(pk=product)
        if product.category.category_name=="Coupons":
            count = VanCouponStock.objects.filter(created_date=datetime.datetime.today().date(),van__pk=van,coupon__coupon_type__coupon_type_name=product.product_name,stock_type__in=["opening_stock","closing"]).aggregate(total_amount=Sum('count'))['total_amount']
        else:
            count = VanProductStock.objects.get(created_date=datetime.datetime.today().date(),van__pk=van,product=product).stock
    except:
        count = 0
    
    return count