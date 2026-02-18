from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'get_salesman',
        'reference_no',
        'invoice_no',
        'invoice_type',
        'invoice_status',
        'invoice_date',          # 👈 ADDED
        'created_date',
        'net_taxable',
        'vat',
        'discount',
        'amout_total',
        'amout_recieved',
        'delete_button',
        'id',
    )

    ordering = ("-created_date",)

    search_fields = (
        'invoice_no',
        'customer__customer_name',
        'customer__custom_id',
    )

    list_filter = (
        'customer',
        'invoice_status',
        'invoice_type',
        'invoice_date',          # 👈 ADDED
        ('created_date', admin.DateFieldListFilter),
    )

    autocomplete_fields = ['customer', 'salesman']

    readonly_fields = ('invoice_no',)  # 🔒 lock invoice number

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

    def get_salesman(self, obj):
        return obj.salesman.get_full_name() if obj.salesman else "-"

    get_salesman.short_description = "Salesman"


class InvoiceItemsAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product_items', 'qty', 'rate')
    search_fields = ('invoice__invoice_no',)  # Enable searching by related invoice number
admin.site.register(InvoiceItems, InvoiceItemsAdmin)

admin.site.register(SuspenseCollection)
