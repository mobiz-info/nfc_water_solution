from django.contrib import admin

from bottle_management.models import Bottle, BottleLedger

# Register your models here.

@admin.register(BottleLedger)
class BottleLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "bottle",
        "action",
        "van",
        "route",
        "customer",
        "reference",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
        "van",
        "route",
    )

    search_fields = (
        "bottle__serial_number",
        "reference",
    )

    ordering = ("-created_at",)

    

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "qr_code",
        "product",
        "status",
        "is_filled",
        "created_at",
        "nfc_uid",
    )

    list_filter = (
        "status",
        "is_filled",
        "product",
        "created_at",
    )

    search_fields = (
        "serial_number",
        "qr_code",
    )

    readonly_fields = (
        "serial_number",
        "created_at",
    )

    ordering = ("-created_at",)

    actions = ["mark_as_damaged", "mark_as_lost"]

    def mark_as_damaged(self, request, queryset):
        queryset.update(status="DAMAGED")
    mark_as_damaged.short_description = "Mark selected bottles as DAMAGED"

    def mark_as_lost(self, request, queryset):
        queryset.update(status="LOST")
    mark_as_lost.short_description = "Mark selected bottles as LOST"
