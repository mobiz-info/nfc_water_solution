import datetime

from django import template
from coupon_management.models import CouponLeaflet

register = template.Library()

@register.filter
def used_coupon_count(sale):
    """Returns the count of used coupon leaflets for the given sale."""
    return CouponLeaflet.objects.filter(coupon=sale.coupon, used=True).count()

@register.filter
def unused_coupon_count(sale):
    """Returns the count of unused coupon leaflets for the given sale."""
    return CouponLeaflet.objects.filter(coupon=sale.coupon, used=False).count()

@register.filter
def per_leaf_rate(sale):
    """Returns the per-leaflet rate."""
    try:
        valuable_leaflets = int(sale.coupon.valuable_leaflets)
        if valuable_leaflets > 0:
            return sale.rate / valuable_leaflets
    except (ValueError, ZeroDivisionError):
        return None
    return None