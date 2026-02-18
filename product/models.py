from django.db import models
import uuid
from master.models import *
from accounts.models import *
from tax_settings.models import *

# Create your models here.

WASHED_TRANSFER_CHOICES = (
        ('used','Used'),
        ('scrap', 'Scrap'),
    )

PRODUCT_TRANSFER_FROM_CHOICES = (
        ('fresh','Fresh'),
        ('used', 'Used'),
    )

PRODUCT_TRANSFER_TO_CHOICES = (
        ('scrap','Scrap'),
        ('service', 'Service'),
    )
SUPERVISOR_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
class ProdutItemMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    product_name = models.CharField(max_length=50,unique=True)
    category = models.ForeignKey('master.CategoryMaster', on_delete=models.CASCADE,null=True,blank=True)
    unit_choices = (
        ('Pcs', 'Pcs'),
        ('Nos', 'Nos'),  # Added 'Nos' as an option
    )
    unit = models.CharField(max_length=50, choices=unit_choices, null=True, blank=True)
    tax = models.ForeignKey('tax_settings.Tax', on_delete=models.CASCADE, null=True, blank=True)
    rate = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_exported = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('product_name',)
    
    def __str__(self):
        return str(self.product_name)

    def get_erp_product_id(self):
        export_status = self.product_export_status.first()
        return export_status.erp_product_id if export_status else None
    

class ProductExportStatus(models.Model):
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE, related_name='product_export_status')
    erp_product_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.product.product_name} with ERP ID {self.erp_product_id}"  
    
      
class Product(models.Model):
    product_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    product_name = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(null=True, blank=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.CASCADE)
    fiveg_status = models.BooleanField(default=False)

    
    class Meta:
            ordering = ('created_date',)

    def __str__(self):
            return str(self.product_name.product_name)
    
class Product_Default_Price_Level(models.Model):
    def_price_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    CUSTOMER_TYPE_CHOICES = (
        ('HOME', 'HOME'),
        ('CORPORATE', 'CORPORATE'),
        ('SHOP', 'SHOP')
    )
    customer_type = models.CharField(max_length=100, choices=CUSTOMER_TYPE_CHOICES, null=True, blank=True)
    product_id = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE, null=True, blank=True)
    rate = models.CharField(max_length=50)
    class Meta:
        ordering = ('customer_type',)

    def __str__(self):
        return str(self.customer_type)
    
class   Staff_Orders(models.Model):
    staff_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=30, null=True, blank=True, unique=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    C_STATUS = (
        ('Order Request', 'Order Request'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
    )
    status = models.CharField(max_length=20, choices=C_STATUS, null=True, blank=True, default='Order Request')
    total_amount = models.CharField(max_length=20, null=True, blank=True)
    VIA_CHOICES = (
        ('Via App', 'Via App'),
        ('Via Staff', 'Via Staff'),
    )
    order_via = models.CharField(max_length=20, choices=VIA_CHOICES, null=True, blank=True, default='Via Staff')
    order_date = models.DateField(null=True, blank=True)
    supervisor_status = models.CharField(max_length=20,choices=SUPERVISOR_STATUS_CHOICES,default='Pending')
    # delivery_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ('order_number',)

    def __str__(self):
        return f'order number : {self.order_number}, created date : {self.created_date}, order date : {self.order_date}'
    
class Staff_Orders_details(models.Model):
    staff_order_details_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    staff_order_id =  models.ForeignKey(Staff_Orders, on_delete=models.SET_NULL, null=True, blank=True,related_name='staff_orders')
    product_id = models.ForeignKey(ProdutItemMaster, on_delete=models.SET_NULL, null=True, blank=True)
    C_STATUS = (
        ('Order Request', 'Order Request'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
    )
    count = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    issued_qty = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    status = models.CharField(max_length=20, choices=C_STATUS, null=True, blank=True, default='Order Request')
    
    class Meta:
        ordering = ('staff_order_details_id',)

    def __str__(self):
        return str(self.staff_order_details_id)

class Staff_IssueOrders(models.Model):
    staff_issuesorder_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=30, null=True, blank=True, unique=True)
    salesman_id = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='salesman_orders',limit_choices_to={'designation_id__designation_name__in': ['Sales Executive', 'Sales Supervisor']})
    staff_Orders_details_id = models.ForeignKey(Staff_Orders_details, on_delete=models.SET_NULL, null=True, blank=True, related_name='salesman_order_details')
    van_route_id = models.ForeignKey('master.RouteMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='van_route_orders')
    product_id = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE, related_name='issued_products')
    coupon_book= models.ForeignKey('coupon_management.NewCoupon',on_delete=models.SET_NULL, null=True, blank=True, related_name='couponsales')
    quantity_issued = models.CharField(max_length=50,null=True, blank=True)
    stock_quantity = models.CharField(max_length=50,null=True, blank=True)
    van = models.ForeignKey('van_management.Van', null=True, blank=True, on_delete=models.SET_NULL)
    
    empty_bottle_count = models.IntegerField(default=0)
    extra_bottle_needed = models.IntegerField(default=0)

    STATUS_CHOICES = (
        ('Order Issued','Order Issued'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order Issued')
    created_by = models.CharField(max_length=20,  blank=True)
    # created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
            ordering = ('staff_issuesorder_id',)

    def __str__(self):
        return str(self.order_number)


class ProductStock(models.Model):
    product_stock_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(null=True, blank=True)
    branch = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='prod_stock_branch')
    status = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product_name.product_name)

class DamageBottleStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
class ScrapProductStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
class WashingProductStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
class ScrapStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.product.product_name)
    
class WashingStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.product.product_name)
    
class WashedProductTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=WASHED_TRANSFER_CHOICES, default='used')
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
class WashedUsedProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.product.product_name)
    
class ScrapcleanedStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)


class ProductionDamageReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason = models.CharField(max_length=20)
    
    created_by = models.CharField(max_length=20)
    modified_by = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.reason)
    
    
class ProductionDamage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    route = models.ForeignKey('master.RouteMaster', on_delete=models.CASCADE)
    branch = models.ForeignKey('master.BranchMaster', on_delete=models.CASCADE)
    reason = models.ForeignKey(ProductionDamageReason, on_delete=models.CASCADE)
    
    product_from = models.CharField(max_length=20,choices=PRODUCT_TRANSFER_FROM_CHOICES)
    product_to = models.CharField(max_length=20,choices=PRODUCT_TRANSFER_TO_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20)
    modified_by = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
    
class NextDayStockRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE, related_name='next_day_stock_request')
    # order_details = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE, related_name='next_day_stock_request')
    van = models.ForeignKey('van_management.Van', null=True, blank=True, on_delete=models.SET_NULL)
    issued_quantity = models.CharField(max_length=50,null=True, blank=True)
    date = models.DateField()
    
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
            ordering = ('id',)

    def __str__(self):
        return str(self.product)
    
class OrderVerifiedSupervisor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Staff_Orders, on_delete=models.CASCADE, related_name='verified_supervisor_details')
    date = models.DateTimeField(auto_now_add=True)
    supervisor = models.ForeignKey('accounts.CustomUser',  null=True, blank=True, on_delete=models.SET_NULL)
    
    damage = models.PositiveIntegerField(default=0)
    leak = models.PositiveIntegerField(default=0)
    service = models.PositiveIntegerField(default=0)
    
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
            ordering = ('id',)
    

    def __str__(self):
        return f'Order: {self.order.order_number}, Verified by: {self.supervisor.get_fullname()}, Date: {self.date}'
    
class OrderVerifiedproductDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_varified_id =  models.ForeignKey(OrderVerifiedSupervisor, on_delete=models.CASCADE)
    
    product_id = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    issued_qty = models.PositiveIntegerField(default=0)
    fresh_qty = models.PositiveIntegerField(default=0)
    used_qty = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return str(self.order_varified_id)
