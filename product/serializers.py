from . models import Product,Product_Default_Price_Level, ProdutItemMaster
from rest_framework import serializers


class ProductSerializers(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    class Meta :
        model = Product
        fields = '__all__'
        
    def get_product_name(self, obj):
        return obj.product_name.product_name


class Product_Default_Price_Level_Serializers(serializers.ModelSerializer):
    class Meta :
        model = Product_Default_Price_Level
        fields = '__all__'
        