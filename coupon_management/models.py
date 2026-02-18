from django.db import models
from django.db import models
import uuid
from datetime import datetime
import qrcode
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files import File

# Create your models here.

COUPON_METHOD_CHOICES = (
    ('digital', 'Digital'),
    ('manual', 'Manual'),
)

class CouponType(models.Model):
    coupon_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_type_name = models.CharField(max_length=20, null=True, blank=True)
    no_of_leaflets = models.CharField(max_length=20, null=True, blank=True)
    valuable_leaflets = models.CharField(max_length=20, null=True, blank=True)
    free_leaflets = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('coupon_type_name',)

    def __str__(self):
        return str(self.coupon_type_name)


class Coupon(models.Model):
    coupon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_type_id= models.ForeignKey(CouponType, on_delete=models.SET_NULL, null=True, blank=True,related_name='coupon_type')
    book_num = models.CharField(max_length=20, null=True, blank=True)
    value_starting_no = models.CharField(max_length=20, null=True, blank=True)
    value_ending_no = models.CharField(max_length=20, null=True, blank=True)
    free_starting_no = models.CharField(max_length=20, null=True, blank=True)
    free_ending_no = models.CharField(max_length=20, null=True, blank=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='user_login')
    status = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    coupon_method = models.CharField(max_length=10,choices=COUPON_METHOD_CHOICES,default='manual',null=True,blank=True)


    class Meta:
        ordering = ('book_num',)

    def __str__(self):
        return str(self.book_num)
    
class CouponRequest(models.Model):
    coupon_request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.CharField(max_length=20, null=True, blank=True)
    coupon_type_id= models.ForeignKey(CouponType, on_delete=models.SET_NULL, null=True, blank=True,related_name='coupon_request')
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='branch_user')
    status = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.coupon_type_id)
    

class AssignStaffCoupon(models.Model):
    assign_id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_request = models.ForeignKey(CouponRequest, on_delete=models.SET_NULL, null=True, blank=True,related_name='coupon_request_request')
    alloted_quantity = models.CharField(max_length=20, null=True, blank=True)
    remaining_quantity = models.CharField(max_length=20, null=True, blank=True)
    R_STATUS = (
        ('Pending', 'Pending'),
        ('Closed', 'Closed'),
       
    )
    status = models.CharField(max_length=20, choices=R_STATUS, null=True, blank=True)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)
    def __str__(self):
        return str(self.assign_id)

class AssignStaffCouponDetails(models.Model):
    assign_coupon_details_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_coupon_assign = models.ForeignKey(AssignStaffCoupon, on_delete=models.SET_NULL, null=True, blank=True,related_name='assign_staff_coupon_request')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True,related_name='id_coupon')
    C_STATUS = (
        ('Pending', 'Pending'),
        ('Assigned to Staff', 'Assigned to Staff'),
        ('Assigned To Customer','Assigned To Customer')
    )
    status = models.CharField(max_length=20, choices=C_STATUS, null=True, blank=True)
    to_customer  = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='coupon_customer')
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.assign_coupon_details_id)
    
#--------------NewCoupon-----------------

class NewCoupon(models.Model):

    coupon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_type = models.ForeignKey(CouponType, on_delete=models.CASCADE, related_name='couponsType')
    book_num = models.CharField(max_length=20, null=True, blank=True)
    no_of_leaflets = models.CharField(max_length=20, null=True, blank=True)
    valuable_leaflets = models.CharField(max_length=20, null=True, blank=True)
    free_leaflets = models.CharField(max_length=20, null=True, blank=True)    
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_login_id')
    status = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    coupon_method = models.CharField(max_length=10,choices=COUPON_METHOD_CHOICES,default='manual',null=True,blank=True)
    qr_code = models.ImageField(upload_to="coupon_qr_codes",null=True, blank=True)

    class Meta:
        ordering = ('book_num',)

    def __str__(self):
        return str(self.book_num)
    
    def coupon_status(self):
        coupon_status = CouponStock.objects.get(couponbook=self)
        return coupon_status.get_coupon_stock_display()

    # def save_qr_code(self):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(str(self.coupon_id))
    #     qr.make(fit=True)

    #     img = qr.make_image(fill_color="blue", back_color="white")
    #     fname = f'coupon_qr_code-{self.book_num}.png'
    #     buffer = BytesIO()
    #     img.save(buffer, 'PNG')
    #     self.qr_code.save(fname, File(buffer), save=False)
    #     img.close()

    # def save(self, *args, **kwargs):
    #     self.save_qr_code()
    #     super().save(*args, **kwargs)
    
class CouponLeaflet(models.Model):
    couponleaflet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE, related_name='leaflets')
    leaflet_number = models.CharField(max_length=10)
    leaflet_name = models.CharField(max_length=20, null=True, blank=True)
    used = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    qr_code = models.ImageField(upload_to="leaflet_qr_codes",null=True, blank=True)

    class Meta:
        ordering = ('leaflet_number',)

    def __str__(self):
        return f"{self.coupon.book_num} - Leaflet {self.leaflet_number} / {self.leaflet_name}"

    # def save_qr_code(self):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
        
    #     # Ensure that leaflet_number is always formatted with leading zeros to maintain a consistent length
    #     formatted_leaflet_number = self.leaflet_number.zfill(2)
        
    #     data_to_encode = f"{self.coupon.book_num}{formatted_leaflet_number}"  # Combine book_num and formatted leaflet_number
    #     qr.add_data(data_to_encode)
    #     qr.make(fit=True)

    #     img = qr.make_image(fill_color="blue", back_color="white")
        
    #     # Adjusted filename format with book_num and formatted leaflet_number
    #     fname = f'leaflet_qr_codes/leaflet_qr_code-{self.coupon.book_num}{formatted_leaflet_number}.png'

    #     buffer = BytesIO()
    #     img.save(buffer, 'PNG')
    #     self.qr_code.save(fname, File(buffer), save=False)
    #     img.close()

    # def save(self, *args, **kwargs):
    #     self.save_qr_code()
    #     super().save(*args, **kwargs)
    
class FreeLeaflet(models.Model):
    couponleaflet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(NewCoupon, on_delete=models.CASCADE)
    leaflet_number = models.CharField(max_length=10)
    leaflet_name = models.CharField(max_length=20, null=True, blank=True)
    used = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    qr_code = models.ImageField(upload_to="leaflet_qr_codes",null=True, blank=True)

    class Meta:
        ordering = ('leaflet_number',)

    def __str__(self):
        return f"{self.coupon.book_num} - Leaflet {self.leaflet_number} / {self.leaflet_name}"
    
    
COUPON_STOCK_CHOICES = (
    ('company', 'Company'),
    ('driver', 'Driver'),
    ('customer', 'Customer'),
    ('used', 'Used'),
    ('van', 'Van'),
)


class CouponStock(models.Model):

    couponstock_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    couponbook = models.ForeignKey(NewCoupon, on_delete=models.CASCADE,null=True, blank=True, related_name='couponbook_stock')
    coupon_stock = models.CharField(max_length=10,choices=COUPON_STOCK_CHOICES,default='company',null=True,blank=True)
    created_by = models.CharField(max_length=20, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-couponstock_id',)
        
    def __str__(self):
        return f"{self.coupon_stock}"