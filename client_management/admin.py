from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html





# Register your models here.
from . models import *

class CustomerCouponStockAdmin(admin.ModelAdmin):
    list_display = ('coupon_type_id', 'coupon_method', 'customer','count')
admin.site.register(CustomerCouponStock,CustomerCouponStockAdmin)

# admin.site.register(CustomerCoupon)
# admin.site.register(CustomerCouponItems)
admin.site.register(ChequeCouponPayment)

@admin.register(CustomerOutstanding)
class CustomerOutstandingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'invoice_no',
        'customer',
        'product_type',
        'outstanding_date',    # 👈 ADDED
        'created_by',
        'created_date',
    )

    ordering = ("-created_date",)

    search_fields = (
        'invoice_no',
        'customer__custom_id',
        'customer__customer_name',
    )

    list_filter = (
        'product_type',
        'outstanding_date',    # 👈 ADDED
        ('created_date', admin.DateFieldListFilter),
    )

    autocomplete_fields = ['customer']

    readonly_fields = ('invoice_no',)  # 🔒 lock reference

    def delete_button(self, obj):
        delete_url = reverse(
            'admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name),
            args=[obj.id]
        )
        return format_html(
            '<a href="{}" class="button" style="color:red;">Delete</a>',
            delete_url
        )

    delete_button.short_description = 'Delete'


admin.site.register(OutstandingProduct)

class CustomerOutstandingAmountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'invoice_no',
        'created_by',
        'created_date',
        'customer',
        'amount'
    )
    search_fields = ('customer_outstanding__invoice_no','customer_outstanding__customer__customer_name',)
    list_filter = ['customer_outstanding__created_date'] 
    ordering = ("-customer_outstanding__created_date",)
    autocomplete_fields = ['customer_outstanding']

    def invoice_no(self, obj):
        return obj.customer_outstanding.invoice_no
    invoice_no.admin_order_field = 'customer_outstanding__invoice_no'
    invoice_no.short_description = 'Invoice No'
    
   
    def created_by(self, obj):
        return obj.customer_outstanding.created_by
    created_by.admin_order_field = 'customer_outstanding__created_by'
    created_by.short_description = 'Created By'

    def created_date(self, obj):
        return obj.customer_outstanding.created_date
    created_date.admin_order_field = 'customer_outstanding__created_date'
    created_date.short_description = 'Created Date'

    def customer(self, obj):
        return obj.customer_outstanding.customer
    customer.admin_order_field = 'customer_outstanding__customer'
    customer.short_description = 'Customer'

admin.site.register(OutstandingAmount, CustomerOutstandingAmountAdmin)

admin.site.register(OutstandingCoupon)
class CustomerOutstandingReportAdmin(admin.ModelAdmin):
    list_display = ('id','product_type','customer','value')
    search_fields = ['customer__custom_id','customer__customer_name']

admin.site.register(CustomerOutstandingReport,CustomerOutstandingReportAdmin)

@admin.register(CustomerSupply)
class CustomerSupplyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_date',
        'supply_date',          # 👈 ADDED
        'customer',
        'invoice_no',
        'salesman',
        'grand_total',
        'allocate_bottle_to_pending',
        'allocate_bottle_to_custody',
        'allocate_bottle_to_paid',
        'discount',
        'net_payable',
        'vat',
        'subtotal',
        'amount_recieved',
        'outstanding_amount_added',
        'outstanding_coupon_added',
        'outstanding_bottle_added',
        'van_stock_added',
        'van_foc_added',
        'van_emptycan_added',
        'custody_added',
    )

    list_filter = (
        'customer__routes',   # route filter
        'salesman',
        'supply_date',        # 👈 filter by supply date
        'created_date',
    )

    search_fields = (
        'customer__customer_name',
        'invoice_no',
    )

    ordering = ('-created_date',)

class CustomerSupplyItemsAdmin(admin.ModelAdmin):

    # Showing fields from CustomerSupplyItems + parent invoice + parent amount_recieved
    list_display = (
        'id',
        'invoice_no',
        'customer_name',
        'product',
        'quantity',
        'rate',
        'amount',
        'foc',
        'amount_recieved',     # From CustomerSupply
        'created_date',
    )

    # Enable invoice search
    search_fields = (
        'customer_supply__invoice_no',
        'customer_supply__customer__customer_name',
    )

    # ====================================================
    # Custom display methods (because parent fields must be accessed)
    # ====================================================
    def invoice_no(self, obj):
        return obj.customer_supply.invoice_no
    invoice_no.short_description = "Invoice No"

    def customer_name(self, obj):
        return obj.customer_supply.customer.customer_name
    customer_name.short_description = "Customer"

    def amount_recieved(self, obj):
        return obj.customer_supply.amount_recieved
    amount_recieved.short_description = "Amount Received"

    def created_date(self, obj):
        return obj.customer_supply.created_date
    created_date.short_description = "Created Date"


admin.site.register(CustomerSupplyItems, CustomerSupplyItemsAdmin)

admin.site.register(CustomerSupplyStock)
admin.site.register(CustomerCart)
admin.site.register(CustomerCartItems)
admin.site.register(CustomerOtherProductChargesChanges)
admin.site.register(CustomerOtherProductCharges)

class DialyCustomersAdmin(admin.ModelAdmin):
    list_display = ('id','date','customer','route','qty','is_emergency','is_supply')
    ordering = ("-date",)
    
    def customer(self, obj):
        return obj.customer.customer_name
    
    def route(self, obj):
        return obj.route.route_name
admin.site.register(DialyCustomers,DialyCustomersAdmin)







@admin.register(CustomerCredit)
class CustomerCreditAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'get_route_name',   # ✅ route name
        'amount',
        'source',
        'created_date',
    )

    list_filter = (
        'source',
        'created_date',
        'customer__routes',  # ✅ route filter
    )

    search_fields = (
        'customer__customer_name',
        'customer__routes__route_name',  # optional
    )

    ordering = ('-created_date',)
    autocomplete_fields = ['customer']

    def get_route_name(self, obj):
        return obj.customer.routes.route_name if obj.customer and obj.customer.routes else '-'

    get_route_name.short_description = 'Route'

@admin.register(CustodyCustom)
class CustodyCustomAdmin(admin.ModelAdmin):
    list_display = (
        "custody_custom_id",
        "customer",
        "agreement_no",
        "total_amount",
        "amount_collected",
        "deposit_type",
        "created_date",
    )

    list_filter = (
        "deposit_type",
        "created_date",
    )

    search_fields = (
        "agreement_no",
        "reference_no",
        "customer__customer_name",
    )

@admin.register(CustodyCustomItems)
class CustodyCustomItemsAdmin(admin.ModelAdmin):
    list_display = (
        "custody_custom",
        "product",
        "quantity",
        "amount",
        "can_deposite_chrge",
        "five_gallon_water_charge",
    )

    search_fields = (
        "custody_custom__agreement_no",
        "custody_custom__customer__customer_name",
        
    )

@admin.register(CustomerCustodyStock)
class CustomerCustodyStockAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "agreement_no",
        "product",
        "quantity",
        "amount",
        "amount_collected",
        "deposit_type",
    )

    list_filter = (
        "deposit_type",
    )

    search_fields = (
        "customer__customer_name",
        "agreement_no",
        "reference_no",
        "serialnumber",
    )

@admin.register(CustomerCoupon)
class CustomerCouponAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "salesman",
        "payment_type",
        "net_amount",
        "amount_recieved",
        "balance",
        "coupon_method",
        "invoice_no",
        "created_date",
    )

    list_filter = (
        "payment_type",
        "coupon_method",
        "created_date",
    )

    search_fields = (
        "invoice_no",
        "reference_number",
        "customer__customer_name", 
        "salesman__username",     
    )

@admin.register(CustomerCouponItems)
class CustomerCouponItemsAdmin(admin.ModelAdmin):
    list_display = (
        "customer_coupon",
        "coupon",
        "rate",
    )

    search_fields = (
        "customer_coupon__invoice_no",
        "coupon__code",   # adjust to REAL field in NewCoupon
    )

@admin.register(CustomerReturn)
class CustomerReturnAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "agreement_no",
        "reference_no",
        "deposit_type",
        "created_by",
        "created_date",
    )
    list_filter = ("deposit_type", "created_date")
    search_fields = ("reference_no", "agreement_no", "customer__name")
    ordering = ("-created_date",)


# ---------------- Customer Return Items ----------------

@admin.register(CustomerReturnItems)
class CustomerReturnItemsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_return",
        "product",
        "quantity",
        "serialnumber",
        "amount",
    )
    list_filter = ("product",)
    search_fields = ("serialnumber", "customer_return__reference_no")
    ordering = ("-id",)


# ---------------- Customer Return Stock ----------------

@admin.register(CustomerReturnStock)
class CustomerReturnStockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "product",
        "quantity",
        "reference_no",
        "deposit_type",
        "amount",
    )
    list_filter = ("deposit_type", "product")
    search_fields = ("reference_no", "agreement_no", "customer__name")
    ordering = ("-id",)