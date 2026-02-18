from datetime import timezone
import random
from django.db import models,transaction, IntegrityError

from django.db.models import Sum,DecimalField,Max
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Customers, CustomUser
from client_management.models import CustomerSupply,CustomerCoupon
from invoice_management.models import Invoice
from master.models import RouteMaster
from coupon_management.models  import Coupon, CouponType

class OrderNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', None)  # Add default value None
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if add and model_instance.order_number is None:  # Check if order_number is None
            last_order = model_instance._meta.model.objects.last()
            if last_order:
                last_order_number = int(last_order.order_number)
                model_instance.order_number = str(last_order_number + 1).zfill(7)
            else:
                model_instance.order_number = '2400000'  # Starting order number
        return super().pre_save(model_instance, add)
    
class SalesExtraModel(models.Model):
    qty_needed = models.IntegerField()
    no_of_coupons = models.IntegerField()
    coupon_variations = models.IntegerField()
    empty_bottles = models.IntegerField()
    collected_bottles = models.IntegerField()
    bottle_variations = models.IntegerField()
    # New status field with choices
    STATUS_CHOICES = (
        ('FOC', 'FOC'),
        ('PENDING', 'PENDING'),
        ('CUSTODY', 'CUSTODY'),
        ('PAID', 'PAID'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    order_number = OrderNumberField()

    def __str__(self):
        return f'SalesExtraModel {self.id}'
    
from django.db import models

class SalesTemp(models.Model):
    invoice_number = models.CharField(max_length=50) 
    data = models.JSONField()


class SaleEntryLog(models.Model):
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    last_delivery_date = models.DateField(null=True, blank=True)
    default_lt_bottle_count = models.IntegerField(null=True, blank=True)
    outstanding_coupons = models.IntegerField(null=True, blank=True, default=None)
    cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    empty_bottles = models.IntegerField(null=True, blank=True, default=None)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    net_taxable = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    received_amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    coupon = models.ForeignKey('coupon_management.Coupon', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    extras = models.ForeignKey(SalesExtraModel, on_delete=models.CASCADE, null=True, blank=True)
    order_number = OrderNumberField()

    def __str__(self):
        return f'SaleEntryLog for {self.customer} - {self.last_delivery_date}'


class OutstandingLog(models.Model):
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    # sale_entry_log = models.ForeignKey(SaleEntryLog, on_delete=models.CASCADE)
    coupons = models.IntegerField(null=True)
    empty_bottles = models.IntegerField(null=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL,null=True, blank=True)
    order_number = OrderNumberField()

    def __str__(self):
        return f"{self.customer} - {self.created_date}"


class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('INCOME', 'INCOME'),
        ('EXPENSE', 'EXPENSE'),
    ]

    TRANSACTION_CATEGORIES = [
        ('FOC', 'FOC'),
        ('PENDING', 'PENDING'),
        ('CUSTODY', 'CUSTODY'),
        ('PAID', 'PAID'),
    ]
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    transaction_category = models.CharField(max_length=20, choices=TRANSACTION_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_staff = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='transactions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    order_number = OrderNumberField()




class CustomerCoupons(models.Model):
    TRANSACTION_TYPE = [
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT'),
    ]
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    routes = models.ForeignKey(RouteMaster, on_delete=models.SET_NULL, null=True, blank=True)
    salesman = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    transaction_id = models.CharField(max_length=20)
    transaction_date = models.DateTimeField(null=True, blank=True)
    coupon_method = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_type = models.ForeignKey(CouponType, on_delete=models.SET_NULL, null=True, blank=True)
    balance_coupons = models.IntegerField(default=0)
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.transaction_id
    

class Transactionn(models.Model):
    transaction_id = models.CharField(max_length=20)
    transaction_date = models.DateTimeField(null=True, blank=True)
    transaction_type = models.ForeignKey(CustomerCoupons, on_delete=models.CASCADE)
    no_of_qty = models.IntegerField(null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    coupons = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

class CollectionPayment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('CASH', 'CASH'),
        ('CHEQUE', 'CHEQUE'),
        ('CARD', 'CARD'),
        ('ONLINE', 'ONLINE') 
    )
    payment_method = models.CharField(max_length=100, choices=PAYMENT_TYPE_CHOICES, null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    salesman = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    amount_received = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    receipt_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=["created_date"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["salesman"]),
        ]
        ordering = ('-id',)

    def __str__(self):
        return str(self.customer)
    
    def total_amount(self):
        return CollectionItems.objects.filter(collection_payment=self).aggregate(total=Sum('amount', output_field=DecimalField()))['total'] or 0
    
    def total_discounts(self):
        collection_items = self.collectionitems_set.all()

        total_discount = 0

        for item in collection_items:
            invoice = item.invoice
            total_discount += invoice.discount
        return total_discount
    
    def total_net_taxeble(self):
        collection_items = self.collectionitems_set.all()

        total_net_taxable = 0

        for item in collection_items:
            invoice = item.invoice
            total_net_taxable += invoice.net_taxable
        return total_net_taxable
    
    def total_vat(self):
        collection_items = self.collectionitems_set.all()

        total_vat = 0

        for item in collection_items:
            invoice = item.invoice
            total_vat += invoice.vat
        return total_vat
    
    def collected_amount(self):
        return CollectionItems.objects.filter(collection_payment=self).aggregate(total=Sum('amount_received', output_field=DecimalField()))['total'] or 0
    
    def is_repeated_customer(self):
        collection_count = CollectionPayment.objects.filter(customer=self.customer,created_date__date=self.created_date.date()).count()
        return collection_count > 1
    
    
class CollectionItems(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    collection_payment = models.ForeignKey(CollectionPayment, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return str(self.collection_payment.customer)

class CollectionCheque(models.Model):
    collection_payment = models.OneToOneField(CollectionPayment, on_delete=models.CASCADE)
    cheque_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    cheque_no = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=20)
    cheque_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'), 
        ('CLEARED', 'CLEARED')
    ]
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='PENDING')
    invoices = models.ManyToManyField(Invoice)

    class Meta:
        ordering = ('-id',)

    def _str_(self):
        return f"{self.bank_name} - {self.cheque_no} ({self.status})"
    
    
class CollectionOnline(models.Model):
    collection_payment = models.OneToOneField(CollectionPayment, on_delete=models.CASCADE)
    transaction_no = models.CharField(max_length=255, null=True, blank=True)
    transaction_date = models.DateField(null=True, blank=True)
    online_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"{self.transaction_no} ({self.status})"
    
class CollectionCard(models.Model):
    collection_payment = models.OneToOneField(CollectionPayment, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=500, null=True, blank=True)
    card_number = models.CharField(max_length=255, null=True, blank=True)
    card_date = models.DateField(null=True, blank=True)
    card_type = models.CharField(max_length=100, null=True, blank=True)
    card_category = models.CharField(max_length=100, null=True, blank=True)
    card_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('CLEARED', 'CLEARED')
    ]
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='PENDING')

    class Meta:
        ordering = ('-id',)

    def _str_(self):
        return f"{self.card_number} ({self.status})"

class SalesmanSpendingLog(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop_in = models.DateTimeField(null=True,blank=True)
    shop_out = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.customer} - {self.created_date}"


class Receipt(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('supply', 'supply'),
        ('collection', 'collection'),
        ('coupon_rechange', 'coupon rechange')
    )
    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_TYPE_CHOICES, null=True, blank=True)
    instance_id = models.CharField(max_length=200)
    amount_received = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    receipt_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_number = models.CharField(max_length=500) 
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    
    created_date = models.DateTimeField()
    
    class Meta:
        ordering = ('-instance_id',)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Instance {self.instance_id}"
    
    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = timezone.now() 
        
        if not self.receipt_number:
            year = self.created_date.strftime("%y")
            prefix = f"RV-{year}/"

            receipt_count = Receipt.objects.filter(
                created_date__year=self.created_date.year,
                receipt_number__startswith=prefix,
            ).count()

            new_number = receipt_count + 1
            self.receipt_number = f"{prefix}{new_number}"

        super().save(*args, **kwargs)



