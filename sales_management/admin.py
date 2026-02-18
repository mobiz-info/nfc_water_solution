import uuid
from django.contrib import admin
from . models import *

# Register your models here.
class CollectionPaymentAdmin(admin.ModelAdmin):
    # Show all fields dynamically
    list_display = [
        'receipt_number','customer','salesman','payment_method','amount_received','total_amount','total_discounts','total_net_taxeble',
        'total_vat','collected_amount','is_repeated_customer','created_date',
    ]

    search_fields = ['receipt_number','customer__customer_name','salesman__username','payment_method',]

    list_filter = ('payment_method','salesman','created_date',)

    autocomplete_fields = ['salesman', 'customer',]

# Admin for CollectionItems
class CollectionItemsAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'amount', 'balance', 'amount_received', 'collection_payment']

    def invoice_number(self, obj):
        return obj.invoice.invoice_number
    invoice_number.short_description = "Invoice Number"

    search_fields = [
        'invoice__invoice_number',
        'collection_payment__receipt_number',
        'collection_payment__customer__customer_name'
    ]

admin.site.register(CollectionPayment, CollectionPaymentAdmin)
admin.site.register(CollectionItems, CollectionItemsAdmin)

admin.site.register(CollectionCheque)
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "transaction_type",
        "customer",
        "invoice_number",
        "amount_received",
        "created_date",
    )

    list_filter = (
        "transaction_type",
        "created_date",
    )

    search_fields = (
        "receipt_number",
        "invoice_number",
        "customer__customer_name",
        "customer__custom_id",
    )

    ordering = ("-created_date",)


