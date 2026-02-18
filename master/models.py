from django.db import models

# Create your models here.
from django.db import models
import uuid
from datetime import datetime
from accounts.models import *
from ckeditor.fields import RichTextField

from accounts.models import Customers

class EmirateMaster(models.Model):
    emirate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    is_exported = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)

class EmirateExportStatus(models.Model):
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.CASCADE, related_name='emirate_export_status')
    erp_emirate_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True) 
     
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.emirate.name} with ERP ID {self.erp_emirate_id}"
    
    
class BranchMaster(models.Model):
    branch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=50, null=True, blank=False)
    address = models.CharField(max_length=100, null=True, blank=False)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    landline = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    trn = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.SET_NULL, null=True, blank=False)
    email = models.CharField(max_length=30, null=True, blank=True)
    user_id = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='master')
    is_exported = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)


class BranchExportStatus(models.Model):
    branch = models.ForeignKey(BranchMaster, on_delete=models.CASCADE, related_name='branch_export_status')
    erp_branch_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True) 
     
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.branch.name} with ERP ID {self.erp_branch_id}"
    
    
class DesignationMaster(models.Model):
    designation_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    designation_name = models.CharField(max_length=50,unique=True)
    is_exported = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('designation_name',)

    def __str__(self):
        return str(self.designation_name)


class DesignationExportStatus(models.Model):
    designation = models.ForeignKey(DesignationMaster, on_delete=models.CASCADE, related_name='designation_export_status')
    erp_designation_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True) 
     
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.designation.designation_name} with ERP ID {self.erp_designation_id}"
    
        
class RouteMaster(models.Model):
    route_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    route_name = models.CharField(max_length=50,unique=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='route_branch')
    is_exported = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('route_name',)

    def __str__(self):
        return str(self.route_name)


class RouteExportStatus(models.Model):
    route = models.ForeignKey(RouteMaster, on_delete=models.CASCADE, related_name='route_export_status')
    erp_route_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True) 
     
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.route.route_name} with ERP ID {self.erp_route_id}"
    
    
class LocationMaster(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    location_name = models.CharField(max_length=50)
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.SET_NULL, null=True, blank=False)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='loc_branch')
    is_exported = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('location_name',)

    def __str__(self):
        return str(self.location_name)

class LocationExportStatus(models.Model):
    location = models.ForeignKey(LocationMaster, on_delete=models.CASCADE, related_name='export_status')
    erp_location_id = models.CharField(max_length=50, unique=True)
    exported_date = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        ordering = ('-exported_date',)

    def __str__(self):
        return f"Exported {self.location.location_name} with ERP ID {self.erp_location_id}"
    
class CategoryMaster(models.Model):
    category_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    category_name = models.CharField(max_length=50,unique=True)
    class Meta:
        ordering = ('category_name',)
    
    def __str__(self):
        return str(self.category_name)
    
class PrivacyPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    content = RichTextField()

    def __str__(self):
        return "Privacy Policy"

class PermissionManagementTab(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tab_name = models.CharField(max_length=255)
    department = models.ForeignKey(DesignationMaster, on_delete=models.CASCADE, related_name='permission_tabs')  
    created_by = models.CharField(max_length=20, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.tab_name)
    
    
class WhatsappData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True, blank=True)
    reciever_no = models.CharField(max_length=20)
    message = models.CharField(max_length=1000)
    
    created_by = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.customer.customer_name)
    
class WhatsappResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whatsapp_data = models.ForeignKey(WhatsappData, on_delete=models.CASCADE)
    send_to = models.CharField(max_length=20)
    message = models.CharField(max_length=1000)
    
    created_by = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.whatsapp_data.customer.customer_name)