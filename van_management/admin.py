from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Van_Routes)
admin.site.register(VanStock)
admin.site.register(VanProductItems)
admin.site.register(VanCouponItems)
admin.site.register(FreelanceVehicleOtherProductChargesChanges)
admin.site.register(FreelanceVehicleOtherProductCharges)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'date_created',
        'expense_date',
        
        'expence_type',
        'amount',
        'route',
    )

    # 🔍 Search fields
    search_fields = (
        'remarks',
        'expence_type__name',   # assuming ExpenseHead has 'name'
        'route__route_name',    # assuming RouteMaster has 'route_name'
        'van__van_number',      # assuming Van model has 'van_number'
    )

    # 🎯 Filters (very useful)
    list_filter = (
        'expense_date',
        'expence_type',
        'route',
        'van',
    )

    # Optional: ordering
    ordering = ('-date_created',)


class OffloadRequestAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','salesman')
admin.site.register(OffloadRequest,OffloadRequestAdmin)

class OffloadRequestItemsAdmin(admin.ModelAdmin):
    list_display = ('quantity','offloaded_quantity','stock_type','product','offload_request')
admin.site.register(OffloadRequestItems,OffloadRequestItemsAdmin)

class OffloadAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','product','quantity','stock_type')
admin.site.register(Offload,OffloadAdmin)

class VanProductStockAdmin(admin.ModelAdmin):
    list_display = ('product','van','created_date','opening_count','change_count','damage_count','empty_can_count','stock','return_count','requested_count','sold_count','closing_count')
admin.site.register(VanProductStock,VanProductStockAdmin)
class VanCouponStockAdmin(admin.ModelAdmin):
    list_display = ('van','coupon','created_date','opening_count','change_count','damage_count','stock','return_count','requested_count','sold_count','closing_count')
admin.site.register(VanCouponStock,VanCouponStockAdmin)

class BottleCountAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','opening_stock','custody_issue','custody_return','qty_added','qty_deducted','closing_stock')
admin.site.register(BottleCount,BottleCountAdmin)

admin.site.register(AuditBase)
admin.site.register(AuditDetails)

@admin.register(Van)
class VanAdmin(admin.ModelAdmin):
    list_display = (
        'van_id',
        'plate',
        'van_make',
        'branch_id',     # ✅ BRANCH ADDED
        'salesman',
        'driver',
        'capacity',
        'bottle_count',
        'van_type',
        'is_exported',
        'created_date',
    )

    list_filter = (
        'branch_id',
        'van_type',
        'is_exported',
        'created_date',
    )

    search_fields = (
        'plate',
        'van_make',
        'branch_id__branch_name',   # ✅ search by branch name (adjust field)
        'salesman__username',
        'salesman__first_name',
        'salesman__last_name',
        'driver__username',
        'driver__first_name',
        'driver__last_name',
    )

   

    ordering = ('-created_date',)