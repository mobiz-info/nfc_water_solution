from django.contrib import admin
from . models import *

# Register your models here.
@admin.register(NewCoupon)
class NewCouponAdmin(admin.ModelAdmin):
    list_display = (
        "book_num",
        "coupon_type",
        "status",
        "created_date",
        "coupon_id",
    )
    search_fields = ("book_num",)
    list_filter = ("coupon_type", "status")
admin.site.register(CouponLeaflet)
admin.site.register(FreeLeaflet)