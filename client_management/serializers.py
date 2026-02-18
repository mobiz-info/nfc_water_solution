from accounts.models import CustomUser,Customers
from client_management.models import CustomerCredit
from rest_framework import serializers
from .models import Vacation
from django.db.models import Sum

class VacationSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    class Meta:
        model = Vacation
        fields = ['vacation_id', 'customer', 'customer_name', 'start_date', 'end_date', 'note']
    
    def get_customer_name(self, obj):
        return obj.customer.customer_name if obj.customer else None
    

class CustomerCreditSerializer(serializers.ModelSerializer):
    customer_id = serializers.UUIDField()
    creditamount = serializers.SerializerMethodField()

    class Meta:
        model = Customers
        fields = ['customer_id', 'customer_name', 'creditamount']

    def get_creditamount(self, obj):
        return (
            CustomerCredit.objects
            .filter(customer=obj)
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        
