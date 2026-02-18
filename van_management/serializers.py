from tax_settings.models import Tax
from . models import *
from rest_framework import serializers



class VanSerializers(serializers.ModelSerializer):
    class Meta :
        model = Van
        fields = '__all__'


class VanRoutesSerializers(serializers.ModelSerializer):
    class Meta :
        model = Van_Routes
        fields = '__all__'


class Van_LicenseSerializers(serializers.ModelSerializer):
    class Meta :
        model = Van_License
        fields = '__all__'
        
# Expense
class ExpenseHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseHead
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    expense_type_name = serializers.CharField(source='expence_type.name', read_only=True)

    class Meta:
        model = Expense
        fields = ('expense_id', 'expence_type', 'expense_type_name', 'route', 'van', 'amount', 'remarks', 'expense_date', 'date_created')

class TaxSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tax
        fields = ('id', 'name','percentage')