from django.db import models
import uuid
from accounts.models import *
from product.models import *
from client_management.models import *

CUSTOMER_REQUEST_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
CUSTOMER_TYPE_REQUEST_CHOICES = [
        ('new', 'New'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ]


class RequestTypeMaster(models.Model):
    
    request_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=50,null=True ,blank= True)
    request_name = models.CharField(max_length=50,unique=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('request_name',)

    def __str__(self):
        return str(self.request_name)
    
class DiffBottlesModel(models.Model):

    diffbottles_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_item = models.ForeignKey(ProdutItemMaster,on_delete=models.CASCADE, null=True, blank=True)
    quantity_required = models.IntegerField(null=True, blank=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    assign_this_to  = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE,null=True,blank=True)
    mode = models.CharField(max_length=10, choices=[('custody', 'Custody'), ('paid', 'Paid')])
    amount = models.CharField(max_length=50,null=True, blank=True)
    discount_net_total = models.CharField(max_length=50,null=True, blank=True)
    created_by = models.CharField(max_length=100,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_bottles')
    status = models.CharField(max_length=20, default='Pending')  
    
    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.customer)
    
class OtherRequirementModel(models.Model):
    requirement_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.ForeignKey(RequestTypeMaster,on_delete=models.SET_NULL, null=True, blank=True)
    requirement = models.TextField(max_length=50)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_otherrequirement')

    class Meta:
        ordering = ('request_type',)

    def __str__(self):
        return str(self.request_type)
    
class CouponPurchaseModel(models.Model):
    COUPON_TYPE_CHOICES = [
        ('manual', 'Manual'),
        ('digital', 'Digital'),
    ]

    CATEGORY_CHOICES = [
        ('cash', 'Cash Coupon'),
        ('credit', 'Credit Coupon'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    couponpurchase_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.ForeignKey(RequestTypeMaster,on_delete=models.SET_NULL, null=True, blank=True)
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)    
    number_of_books = models.IntegerField(null=True)
    payment_status = models.CharField(max_length=10,choices=PAYMENT_STATUS_CHOICES,default='unpaid',)
    amount = models.CharField(max_length=50,null=True, blank=True)
    free_coupon = models.IntegerField(default=0)
    discount = models.CharField(max_length=50,null=True, blank=True)
    delivery_date = models.DateField(blank=True,null=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_couponpurchase')

    class Meta:
        ordering = ('request_type',)

    def __str__(self):
        return str(self.request_type)
    
class CustodyPullOutModel(models.Model): 
    custodypullout_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.ForeignKey(RequestTypeMaster,on_delete=models.SET_NULL, null=True, blank=True)
    customer_custody_item = models.ForeignKey('client_management.CustodyCustomItems', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_custody_item')
    item_name = models.ForeignKey('product.Product', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_product')
    qty_to_be_taken_out = models.IntegerField(default=0)
    scheduled_date = models.DateField(blank=True, null=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_custodypullout')

    class Meta:
        ordering = ('item_name',)

    def __str__(self):
        return str(self.item_name)

class CustomerComplaint(models.Model): 

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    category = models.CharField(max_length=20,default=0)
    subcategory = models.CharField(max_length=20,default=0)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    complaint= models.CharField(max_length=500)
    status = models.CharField(max_length=30, default='Pending')
  
    
    def __str__(self):
        return f"{self.id}"
    

class CustomerRegistrationRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50,default=0)
    phone_no = models.CharField(max_length=50,default=0)
    building_name = models.CharField(max_length=50,default=0)
    room_or_flat_no = models.CharField(max_length=50,default=0)
    floor_no = models.CharField(max_length=10, default=0)  
    email_id = models.EmailField(max_length=100, blank=True, null=True)  
    no_of_5g_bottles_required = models.IntegerField(default=0)
    visit_schedule = models.JSONField(null=True,blank=True)
    status = models.CharField(max_length=50,default="requested",choices=CUSTOMER_REQUEST_CHOICES)
    
    location = models.ForeignKey('master.LocationMaster', on_delete=models.CASCADE)
    emirate = models.ForeignKey('master.EmirateMaster', on_delete=models.CASCADE)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)

class CustomerRequestType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50,default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)


class CustomerRequests(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_requests')
    request_type = models.ForeignKey(CustomerRequestType,on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50,default="new",choices=CUSTOMER_TYPE_REQUEST_CHOICES)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('-created_date',)
    

    def __str__(self):
        return f"Request {self.id} -{self.request_type} - {self.customer} - {self.status}"

class CustomerRequestStatus(models.Model):


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_request = models.ForeignKey(CustomerRequests,on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50,default="new",choices=CUSTOMER_TYPE_REQUEST_CHOICES)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f"Request {self.customer_request} - {self.status} on {self.created_date}"
    
class CustomerRequestCancelReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_request = models.ForeignKey(CustomerRequests,on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=50,default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f"Cancel Reason for Request {self.customer_request.id}-{self.reason}"