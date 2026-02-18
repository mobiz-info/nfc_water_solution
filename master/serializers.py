from django.db.models import Sum

from rest_framework import serializers

from . models import *
from accounts.models import CustomUser
from client_management.models import CustomerCoupon, CustomerSupply, CustomerSupplyItems


class RouteMasterSerializers(serializers.ModelSerializer):
    van_id = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteMaster
        fields = '__all__'

    def get_van_id(self, obj):
        van_route = obj.van_routes.first()  
        return van_route.van.van_id if van_route and van_route.van else None


class LocationMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = LocationMaster
        fields = '__all__'


class DesignationMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = DesignationMaster
        fields = '__all__'


class BranchMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = BranchMaster
        fields = '__all__'

class CategoryMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = CategoryMaster
        fields = '__all__'


class EmirateMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = EmirateMaster
        fields = '__all__'
        
        
class EmiratesBasedLocationsSerializers(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()
    class Meta :
        model = EmirateMaster
        fields = ['emirate_id','name','locations']
        
    def get_locations(self,obj):
        branch_id = self.context.get('branch_id')
        
        instances = LocationMaster.objects.filter(emirate=obj)
        if branch_id:
            instances = instances.filter(branch_id__pk=branch_id)
        return LocationMasterSerializers(instances, many=True).data
    
    
class SalesmanSupplyCountSerializer(serializers.ModelSerializer):
    salesman_name = serializers.SerializerMethodField()
    supply_count = serializers.SerializerMethodField()
    empty_bottle_count = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['salesman_name', 'supply_count', 'empty_bottle_count']
    
    def get_salesman_name(self, obj):
        return obj.username
    
    def get_supply_count(self, obj):
        date = self.context.get('date')
        return CustomerSupplyItems.objects.filter(customer_supply__salesman=obj,customer_supply__created_date__date=date,product__product_name="5 Gallon").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    def get_empty_bottle_count(self, obj):
        date = self.context.get('date')
        return CustomerSupply.objects.filter(salesman=obj,created_date__date=date).aggregate(total_qty=Sum('collected_empty_bottle'))['total_qty'] or 0
    

class SalesmanRechargeCountSerializer(serializers.ModelSerializer):
    salesman_name = serializers.SerializerMethodField()
    coupon_count = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['salesman_name', 'coupon_count']
    
    def get_salesman_name(self, obj):
        return obj.username
    
    def get_coupon_count(self, obj):
        date = self.context.get('date')
        return CustomerCoupon.objects.filter(salesman=obj,created_date__date=date).count()