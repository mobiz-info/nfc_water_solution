from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(ProdutItemMaster)
admin.site.register(Product)
admin.site.register(ProductStock)
admin.site.register(Product_Default_Price_Level)
admin.site.register(ScrapStock)
admin.site.register(WashingStock)
admin.site.register(WashedProductTransfer)
admin.site.register(WashedUsedProduct)
admin.site.register(ScrapcleanedStock)
admin.site.register(ProductionDamageReason)

class StaffOrdersAdmin(admin.ModelAdmin):
    list_display = ["order_number","created_by","created_date","order_date"]
admin.site.register(Staff_Orders,StaffOrdersAdmin)

class StaffOrdersDetailsAdmin(admin.ModelAdmin):
    list_display = ["created_date","staff_order_id","product_id","count","issued_qty","status"]
admin.site.register(Staff_Orders_details,StaffOrdersDetailsAdmin)

class Staff_IssueOrdersAdmin(admin.ModelAdmin):
    list_display = ["order_number","salesman_id","staff_Orders_details_id","van_route_id","product_id","coupon_book","quantity_issued","stock_quantity","van","status"]
admin.site.register(Staff_IssueOrders,Staff_IssueOrdersAdmin)