import datetime
from django.conf import settings

from rest_framework import serializers

from master.models import *
from accounts.models import *
from client_management.models import *
from van_management.models import *

class RouteMasterSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteMaster
        fields = ['route_id','route_name','branch_id','branch_name']
        
    def get_branch_name(self,obj):
        return obj.branch_id.name


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteExportStatus
        fields = ['route', 'erp_route_id']
            
    
class BranchMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchMaster
        fields = ['branch_id','name','address','mobile','landline','phone','fax','trn','website','emirate','email','user_id','logo']
        
    
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchExportStatus
        fields = ['branch', 'erp_branch_id']
               
class EmirateMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmirateMaster
        fields = ['emirate_id','name']

class EmirateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmirateExportStatus
        fields = ['emirate', 'erp_emirate_id']        
        
class DesignationMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DesignationMaster
        fields = ['designation_id','designation_name']
        
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignationExportStatus
        fields = ['designation', 'erp_designation_id']  
        
class LocationMasterSerializer(serializers.ModelSerializer):
    emirate_name = serializers.SerializerMethodField()
    emirate_id = serializers.PrimaryKeyRelatedField(source='emirate', read_only=True)
    
    class Meta:
        model = LocationMaster
        fields = ['location_id','location_name','emirate_name','emirate_id']
        
    def get_emirate_name(self, obj):
        return obj.emirate.name if obj.emirate else None

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationExportStatus
        fields = ['location', 'erp_location_id']
        
class CustomUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    route_name = serializers.SerializerMethodField()
    salesman = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'route_name', 'salesman', 'staff_id', 'full_name', 'email', 'user_type', 'branch_id', 'designation_id', 
            'phone', 'blood_group', 'permanent_address', 'present_address', 'labour_card_no', 
            'labour_card_expiry', 'driving_licence_no', 'driving_licence_expiry', 'licence_issued_by', 
            'visa_issued_by', 'visa_no', 'visa_expiry', 'emirates_id_no', 'emirates_expiry', 
            'health_card_no', 'health_card_expiry', 'base_salary', 'wps_percentage', 'wps_ref_no', 
            'insurance_no', 'insurance_expiry', 'insurance_company', 'user_management', 
            'product_management', 'masters', 'van_management', 'coupon_management', 
            'client_management', 'nationality', 'visa_type', 'joining_date', 'passport_expiry', 
            'passport_number'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name and obj.last_name else obj.username

    def get_route_name(self, obj):
        van = Van.objects.filter(salesman=obj).first()
        if van:
            van_route = Van_Routes.objects.filter(van=van).first()
            if van_route and van_route.routes:
                return van_route.routes.route_name  # assuming RouteMaster has this field
        return None

    def get_salesman(self, obj):
        return self.get_full_name(obj)

    
class CustomUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserExportStatus
        fields = ['emp', 'erp_emp_id']

class CustomersSerializer(serializers.ModelSerializer):
    routes_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    emirate_name = serializers.SerializerMethodField()

    class Meta:
        model = Customers
        fields = [
            'customer_id', 'custom_id', 'customer_name', 'building_name', 'door_house_no',
            'mobile_no', 'email_id', 'routes_name', 'sales_type',
            'no_of_bottles_required', 'emirate_name', 'location_name'
        ]

    def get_routes_name(self, obj):
        return obj.routes.route_name if obj.routes else None

    def get_location_name(self, obj):
        return obj.location.location_name if obj.location else None

    def get_emirate_name(self, obj):
        return obj.emirate.name if obj.emirate else None
   
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerExportStatus
        fields = ['customer', 'erp_customer_id']
        

class ProdutItemMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutItemMaster
        fields = [
            'id', 'product_name', 'category', 'unit', 'tax', 'rate', 'image'
        ] 

class ProdutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductExportStatus
        fields = ['product', 'erp_product_id']
        
        
        
class VanSerializers(serializers.ModelSerializer):
    total_vanstock = serializers.SerializerMethodField()
    van_route = serializers.SerializerMethodField()
    
    class Meta:
        model = Van
        fields = [
            'van_id','van_make', 'plate', 'renewal_date', 'insurance_expiry_date', 'capacity',
            'bottle_count', 'driver', 'salesman', 'branch_id', 'van_type',
            'total_vanstock', 'van_route'
        ]
    
    def get_total_vanstock(self, obj):
        request = self.context.get('request')
        date = request.query_params.get('date') if request else None
        return obj.get_total_vanstock(date)
    
    def get_van_route(self, obj):
        return obj.get_van_route()
    
class VansSerializer(serializers.ModelSerializer):
    class Meta:
        model = VanExportStatus
        fields = ['van', 'erp_van_id']