from rest_framework import serializers
from .models import Order_change, Order_return, Change_Reason

class ChangeReasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Change_Reason
        fields = ['reason_name']
        
class OrderChangeSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    route_name = serializers.CharField(source='route.route_name', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    reason_name = serializers.CharField(source='reason.reason_name', read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(
        queryset=Change_Reason.objects.all(), write_only=True, source='reason'
    )
    
    class Meta:
        model = Order_change
        fields = '__all__'
    
    def update(self, instance, validated_data):
        # Call superclass's update method
        super().update(instance, validated_data)
        return instance

class OrderReturnSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    reason_name = serializers.CharField(source='reason.reason_name', read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(
        queryset=Change_Reason.objects.all(), write_only=True, source='reason'
    )

    class Meta:
        model = Order_return
        fields = [
            'order_return_id','customer','customer_name','route','route_name','product','product_name','reason','reason_id',
            'reason_name','note','returned_quantity','return_date',
        ]

class ChangeReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Change_Reason
        fields = '__all__'
