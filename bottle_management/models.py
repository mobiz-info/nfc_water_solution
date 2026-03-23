from django.db import models
from django.utils import timezone

from accounts.models import Customers
from product.models import Product, ProdutItemMaster
from van_management.models import Van

# Create your models here.
class Bottle(models.Model):
    STATUS_CHOICES = [
        ("GODOWN", "In Godown"),
        ("VAN", "In Van"),
        ("CUSTOMER", "With Customer"),
        ("DAMAGED", "Damaged"),
        ("LOST", "Lost"),
    ]

    serial_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="GODOWN"
    )
    nfc_uid = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    qr_code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    current_customer = models.ForeignKey(
        Customers,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bottles"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=30, blank=True)
    current_van = models.ForeignKey(
        Van,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bottles"
    )
    
    is_filled = models.BooleanField(default=False)

    current_route = models.ForeignKey(
        "master.RouteMaster",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bottles"
    )

    bottle_cycle = models.IntegerField(default=0)
    visited_customer_in_current_cycle = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.serial_number

    

class BottleLedger(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Created"),
        ("LOAD_TO_VAN", "Loaded To Van"),
        ("EMPTY_BOTTLE_ALLOCATION", "Empty Bottle Allocation"),
        ("SUPPLY", "Supplied To Customer"),
        ("RETURN", "Returned From Customer"),
        ("OFFLOAD", "Offloaded To Godown"),
        ("DAMAGE", "Damaged"),
        ("LEAK", "Leaked"),
        ("SERVICE", "Sent For Service"),
        ("CUSTODY_ADD", "Custody Add"),
        ("CUSTODY_PULLOUT", "Custody Pullout"),
        ("UNLOAD_FROM_VAN", "Unload From Van"),
        ("FOC", "Free Of Cost"),
        ("REFILL", "Refilled"),
        ("CREATE_WITH_NFC", "Created with NFC"),
    ]

    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    customer = models.ForeignKey(
        Customers,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    van = models.ForeignKey(
        Van,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    reference = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=30, blank=True)
    
    route = models.ForeignKey(
        "master.RouteMaster",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bottle_ledgers"
    )
