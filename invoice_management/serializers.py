from master.models import CategoryMaster
from product.models import Product
from rest_framework import serializers

from accounts.models import Customers

class BuildingNameSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Customers
        fields = ['building_name']
        
        
class CustomersSerializers(serializers.ModelSerializer):
    route_name = serializers.SerializerMethodField()
    outstanding_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Customers
        fields = ['customer_name','customer_id','mobile_no','building_name','door_house_no','route_name','outstanding_amount']
        
    def get_route_name(self,instance):
        return instance.routes.route_name
    
    def get_outstanding_amount(self,instance):
        return 0
    
    
class ProductSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['product_id','product_name']
        
