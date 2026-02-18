from datetime import timedelta
import uuid
from django.utils.timezone import now
from django.db import models
from django.db.models import Sum
from decimal import Decimal


from accounts.models import Customers,CustomUser
from master.models import *
from order.models import Change_Reason
from product.models import Product, ProductionDamageReason, ProdutItemMaster
from coupon_management.models import Coupon, CouponType, NewCoupon

# Create your models here.
STOCK_TYPES = (
        ('opening_stock', 'Opening Stock'),
        ('change', 'Change'),
        ('return', 'Return'),
        ('closing', 'Closing'),
        ('damage', 'Damage'),
        ('emptycan','Empty Can')
    )
SALESMAN_CUSTOMER_TYPE_REQUEST_CHOICES = [
        ('new', 'New'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ]
VAN_TYPE_CHOICES = [
        ('company', 'Company'),
        ('freelance', 'Freelance'),
    ]
ISSUE_STATUS=[
    ('paid','Paid'),
    ('non_paid', 'Non Paid'),
]
class Van(models.Model):
    van_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    van_make = models.CharField(max_length=50)
    plate = models.CharField(max_length=50)
    renewal_date = models.DateTimeField(blank=True, null=True)
    insurance_expiry_date = models.DateTimeField(blank=True, null=True)
    capacity = models.IntegerField(default=0)
    bottle_count = models.PositiveIntegerField(default=0)
    driver = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,related_name='driver_van')
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,related_name='salesman_van')
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='van_branch')
    van_type = models.CharField(max_length=10, choices=VAN_TYPE_CHOICES, default='company')
    is_exported = models.BooleanField(default=False)

    class Meta:
        ordering = ('van_make',)

    def __str__(self):
        return str(self.van_make)
    
    def get_total_vanstock(self,date):
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
        
        product_count = VanProductStock.objects.filter(created_date=date,van=self).aggregate(total_amount=Sum('stock'))['total_amount'] or 0
        coupon_count = VanCouponStock.objects.filter(created_date=date,van=self).aggregate(total_amount=Sum('stock'))['total_amount'] or 0
        return product_count + coupon_count
    
    def get_van_route(self):
        try:
            return Van_Routes.objects.filter(van=self).first().routes.route_name
        except:
            return "No Route Assigned"
    
    def get_vans_routes(self):
        van_route = Van_Routes.objects.filter(van=self).first()
        if van_route and van_route.routes:
            return van_route.routes.route_name
        return "No Route Assigned"


class VanExportStatus(models.Model):
    van = models.ForeignKey(Van, on_delete=models.CASCADE, related_name='van_export_status')
    erp_van_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.van.van_make} with ERP ID {self.erp_van_id}"  
    
        
class Van_Routes(models.Model):
    van_route_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    van = models.ForeignKey(Van, on_delete=models.CASCADE, null=True, blank=True,related_name='van_master')
    routes = models.ForeignKey(RouteMaster, on_delete=models.SET_NULL, null=True, blank=True,related_name='van_routes')

    class Meta:
        ordering = ('van',)

    def __str__(self):
        return str(self.van)

class Van_License(models.Model):
    van_license_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    van = models.ForeignKey(Van, on_delete=models.CASCADE, null=True, blank=True,related_name='van_license')
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.SET_NULL, null=True, blank=True,related_name='license_emirate')
    license_no = models.CharField(max_length=50, null=True, blank=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('van',)

    def __str__(self):
        return str(self.van)


class ExpenseHead(models.Model):
    expensehead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    expense_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expence_type = models.ForeignKey(ExpenseHead, on_delete=models.CASCADE)
    route = models.ForeignKey(RouteMaster, blank=True, null=True, on_delete=models.SET_NULL)
    van = models.ForeignKey(Van, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True)
    expense_date = models.DateField()
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.expence_type} - {self.amount}"
    
class VanStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    stock_type = models.CharField(max_length=100,choices=STOCK_TYPES)


    def __str__(self):
        return f"{self.id}"
    

       
class VanProductItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    van_stock = models.ForeignKey(VanStock, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"
    
class VanCouponItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE)
    book_no = models.CharField(max_length=100)
    coupon_type = models.ForeignKey(CouponType, on_delete=models.CASCADE)
    van_stock = models.ForeignKey(VanStock, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"
    
# class VanProductStock(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
#     stock_type = models.CharField(max_length=100,choices=STOCK_TYPES)
#     count = models.PositiveIntegerField(default=0)
#     van = models.ForeignKey(Van, on_delete=models.CASCADE,null=True,blank=True)

#     def __str__(self):
#         return f"{self.id}"

class VanProductStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateField()
    opening_count = models.PositiveIntegerField(default=0)
    closing_count = models.PositiveIntegerField(default=0)
    change_count = models.PositiveIntegerField(default=0)
    damage_count = models.PositiveIntegerField(default=0)
    empty_can_count = models.PositiveIntegerField(default=0)
    return_count = models.PositiveIntegerField(default=0)
    requested_count = models.PositiveIntegerField(default=0)
    pending_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    foc = models.PositiveIntegerField(default=0)
    
    product = models.ForeignKey(ProdutItemMaster,on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE,null=True,blank=True)
    excess_bottle = models.PositiveIntegerField(default=0)  # New field added


    def __str__(self):
        return f"{self.id}"
    
    # def save(self, *args, **kwargs):
    #     # offload_count = Offload.objects.filter(van=self.van,product=self.product,created_date__date=self.created_date).aggregate(total_count=Sum('quantity'))['total_count'] or 0
    #     # if self.stock > 0:
    #     # self.closing_count = self.stock + self.empty_can_count + self.return_count
    #     self.closing_count = self.stock

    #     super(VanProductStock, self).save(*args, **kwargs)
        
class VanCouponStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateField()
    opening_count = models.PositiveIntegerField(default=0)
    closing_count = models.PositiveIntegerField(default=0)
    change_count = models.PositiveIntegerField(default=0)
    damage_count = models.PositiveIntegerField(default=0)
    return_count = models.PositiveIntegerField(default=0)
    requested_count = models.PositiveIntegerField(default=0)
    pending_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    used_leaf_count = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f"{self.id}"
    
    def save(self, *args, **kwargs):
        self.closing_count = self.stock
        
        super(VanCouponStock, self).save(*args, **kwargs)
    
    
class Offload(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    stock_type = models.CharField(max_length=100,choices=STOCK_TYPES)
    offloaded_date=models.DateField(blank=True, null=True)
    def __str__(self):
        return f"{self.id}"
    
class OffloadCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE,blank=True, null=True)
    van = models.ForeignKey(Van, on_delete=models.CASCADE,blank=True, null=True)
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    stock_type = models.CharField(max_length=100,choices=STOCK_TYPES)

    def __str__(self):
        return f"{self.id}"
    
class OffloadReturnStocks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    scrap_count = models.PositiveIntegerField(default=0)
    washing_count = models.PositiveIntegerField(default=0)
    other_quantity= models.PositiveIntegerField(default=0)
    other_reason= models.CharField(max_length=300)
    def __str__(self):
        return f"{self.id}"
    
class OffloadDamageStocks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    scrap_count = models.PositiveIntegerField(default=0)
    washing_count = models.PositiveIntegerField(default=0)
    other_quantity= models.PositiveIntegerField(default=0)
    other_reason= models.CharField(max_length=300)
    def __str__(self):
        return f"{self.id}"
       
class SalesmanRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='salesman_requests_created')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='salesman_requests')
    request = models.TextField()

    def __str__(self):
        return f"{self.id}"
    

class BottleAllocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    route = models.ForeignKey(RouteMaster, blank=True, null=True, on_delete=models.SET_NULL)
    fivegallon_count = models.PositiveIntegerField(default=0)
    reason =models.CharField(max_length=300)


    def __str__(self):
        return f"{self.id}"

class StockMovement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    from_van = models.ForeignKey(Van, on_delete=models.CASCADE,related_name='from_van')
    to_van = models.ForeignKey(Van, on_delete=models.CASCADE,related_name='to_van')


    def __str__(self):
        return f"{self.id}"
    
class StockMovementProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    stock_movement = models.ForeignKey(StockMovement, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.id}"
    
STOCK= (
    ('fresh','Fresh'),
    ('used','Used'),
)
    
class BottleCount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=100, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    opening_stock = models.PositiveIntegerField(default=0)
    custody_issue = models.PositiveIntegerField(default=0)
    custody_return = models.PositiveIntegerField(default=0)
    qty_added = models.PositiveIntegerField(default=0)
    qty_deducted = models.PositiveIntegerField(default=0)
    closing_stock = models.PositiveIntegerField(default=0)
    comment = models.TextField()
    
    van = models.ForeignKey(Van,on_delete=models.CASCADE)
    
    class Meta:
        ordering = ('-created_date',)
    
    def save(self, *args, **kwargs):
        self.closing_stock = max(0, (
        self.opening_stock 
        + self.qty_added 
        + self.custody_return 
        - self.qty_deducted 
        - self.custody_issue
        ))
        super(BottleCount, self).save(*args, **kwargs)

        
    # def save(self, *args, **kwargs):
    #     self.closing_stock = (
    #         self.opening_stock 
    #         + self.qty_added 
    #         + self.custody_return 
    #         - self.qty_deducted 
    #         - self.custody_issue
    #     )
    #     super(BottleCount, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.id)
    
class EmptyCanStock(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return f"{self.id}" 
    
      
class OffloadRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE,null=True, blank=True)
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    date=models.DateField(blank=True, null=True)
    status=models.BooleanField(default=False)
    
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.van)
    
class OffloadRequestItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.PositiveIntegerField(default=0)
    offloaded_quantity = models.PositiveIntegerField(default=0)
    stock_type = models.CharField(max_length=100)
    
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True, blank=True)
    offload_request = models.ForeignKey(OffloadRequest, on_delete=models.CASCADE,null=True, blank=True)
    
    class Meta:
        ordering = ('offload_request__created_date',)

    def __str__(self):
        return str(self.product.product_name)
    
class OffloadRequestReturnStocks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    other_reason= models.CharField(max_length=300)
    scrap_count = models.PositiveIntegerField(default=0)
    washing_count = models.PositiveIntegerField(default=0)
    other_quantity= models.PositiveIntegerField(default=0)
    
    offload_request_item = models.ForeignKey(OffloadRequestItems, on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"{self.id}"
    
class OffloadRequestCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.PositiveIntegerField(default=0)
    stock_type = models.CharField(max_length=100,choices=STOCK_TYPES)
    
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE)
    offload_request = models.ForeignKey(OffloadRequest, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"
    

class ExcessBottleCount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=30, blank=True)
    bottle_count = models.PositiveIntegerField()
    route = models.ForeignKey(RouteMaster, on_delete=models.CASCADE)

    def __str__(self):
        return f"Excess bottles for {self.van} on {self.created_date}"
    

class CustomerProductReturn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    reason= models.ForeignKey(Change_Reason, on_delete=models.CASCADE)
    quantity= models.PositiveIntegerField(default=0)
    note = models.TextField()
    
    def __str__(self):
        return f"{self.id}"
    
class CustomerProductReplace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    reason= models.ForeignKey(Change_Reason, on_delete=models.CASCADE)
    quantity= models.PositiveIntegerField(default=0)
    note = models.TextField()
    
    def __str__(self):
        return f"{self.id}"
    

class VanSaleDamage(models.Model):
    DAMAGE_FROM_CHOICES = [
        ('fresh_stock', 'Fresh Stock'),
        ('empty_can', 'Empty Can'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    reason = models.ForeignKey(ProductionDamageReason, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    damage_from = models.CharField(max_length=20, choices=DAMAGE_FROM_CHOICES, default="empty_can")  # 👈 added field

    created_by = models.CharField(max_length=20)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return f"{self.product.product_name} - {self.damage_from}"
    
class DamageControl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    route = models.ForeignKey(RouteMaster, blank=True, null=True, on_delete=models.SET_NULL)
    damage = models.PositiveIntegerField(default=0) 
    leak = models.PositiveIntegerField(default=0)  
    service_bottle = models.PositiveIntegerField(default=0)  
    
    class Meta:
        ordering = ["-created_date", "route"]

    def __str__(self):
        return f"DamageControl - Route: {self.route.route_name}, Date: {self.created_date}"
    
class SalesmanCustomerRequestType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50,default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)
    
class SalesmanCustomerRequests(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True)
    request_type = models.ForeignKey(SalesmanCustomerRequestType,on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50,default="new",choices=SALESMAN_CUSTOMER_TYPE_REQUEST_CHOICES)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('-created_date',)
    

    def __str__(self):
        return f"Request {self.id} -{self.request_type} - {self.customer} - {self.status}"

class SalesmanCustomerRequestStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salesman_customer_request = models.ForeignKey(SalesmanCustomerRequests,on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50,default="new",choices=SALESMAN_CUSTOMER_TYPE_REQUEST_CHOICES)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f"Request {self.customer_request} - {self.status} on {self.created_date}"
    
class SalesmanCustomerRequestCancelReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salesman_customer_request = models.ForeignKey(SalesmanCustomerRequests,on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=50,default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f"Cancel Reason for Request {self.customer_request.id}-{self.reason}"
    

class AuditBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True) 
    
    route = models.ForeignKey(RouteMaster, on_delete=models.CASCADE,null=True, blank=True)
    marketing_executieve = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='marketing_audits',null=True, blank=True)
    salesman = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='salesman_audits',null=True, blank=True)
    helper  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='helper_audits',null=True, blank=True)
    driver   = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='driver_audits',null=True, blank=True)
    
    
    def __str__(self):
        return f"Audit {self.id} - {self.route.route_name} ({self.start_date} to {self.end_date})"
    
class AuditDetails(models.Model):
    audit_base = models.ForeignKey(AuditBase, on_delete=models.CASCADE, related_name='audit_details')
    customer    = models.ForeignKey(Customers, on_delete=models.CASCADE)
    
    previous_outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    previous_bottle_outstanding = models.IntegerField(null=True, blank=True)
    bottle_outstanding = models.IntegerField(null=True, blank=True)

    previous_outstanding_coupon = models.IntegerField(null=True, blank=True)
    outstanding_coupon = models.IntegerField(null=True, blank=True)
    
    previous_hot_and_cold_dispenser = models.IntegerField(null=True, blank=True)
    hot_and_cold_dispenser = models.IntegerField(null=True, blank=True)

    previous_table_dispenser = models.IntegerField(null=True, blank=True)
    table_dispenser = models.IntegerField(null=True, blank=True)

    # Remarks
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Audit Detail - {self.customer.customer_name} (Audit {self.audit_base.id})"
    
    def get_amount_variation(self):
        prev = self.previous_outstanding_amount or Decimal("0.00")
        cur = self.outstanding_amount or Decimal("0.00")
        return prev - cur

    def get_bottle_variation(self):
        prev = self.previous_bottle_outstanding or 0
        cur = self.bottle_outstanding or 0
        return prev - cur

    def get_coupon_variation(self):
        prev = self.previous_outstanding_coupon or 0
        cur = self.outstanding_coupon or 0
        return prev - cur

    def get_hot_and_cold_variation(self):
        prev = self.previous_hot_and_cold_dispenser or 0
        cur = self.hot_and_cold_dispenser or 0
        return prev - cur

    def get_table_dispenser_variation(self):
        prev = self.previous_table_dispenser or 0
        cur = self.table_dispenser or 0
        return prev - cur
    
    
class FreelanceVehicleRateChange(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    old_rate = models.DecimalField(max_digits=10, decimal_places=2)
    new_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ('van',)

    def __str__(self):
        return str(self.van)
    
class FreelanceVehicleOtherProductChargesChanges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    product_item = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    privious_rate = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    current_rate = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    created_by = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=200, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.van}"
    
class FreelanceVehicleOtherProductCharges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    product_item = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    current_rate = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.van}"    
    
class FreelanceVanOutstanding(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    class Meta:
        ordering = ('van',)

    def __str__(self):
        return str(self.van)
    
class FreelanceVanProductIssue(models.Model):
    issue_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey(Van, on_delete=models.CASCADE, related_name="product_issues")
    product = models.ForeignKey('product.ProdutItemMaster', on_delete=models.CASCADE, related_name="product_issues")
    empty_bottles = models.PositiveIntegerField(default=0)  
    extra_bottles = models.PositiveIntegerField(default=0)  
    total_bottles_issued = models.IntegerField(default=0)  
    issued_by = models.CharField(max_length=50)
    issued_date = models.DateTimeField(default=now)
    status = models.CharField(max_length=50,choices=ISSUE_STATUS)

    def save(self, *args, **kwargs):
        self.total_bottles_issued = self.empty_bottles + self.extra_bottles
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.van} - {self.total_bottles_issued} Bottles Issued"