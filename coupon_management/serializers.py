from rest_framework import serializers
from . models import *
from product.models import *


class couponTypeserializers(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()

    class Meta :
        model = CouponType
        fields = ('coupon_type_id','coupon_type_name','no_of_leaflets','valuable_leaflets','free_leaflets','rate')
    
    def get_rate(self,obj):
        try:
            rate = ProdutItemMaster.objects.get(product_name=obj.coupon_type_name).rate
        except:
            rate = 0
        return rate

class couponTypeCreateserializers(serializers.ModelSerializer):

    class Meta :
        model = CouponType
        fields = '__all__'
        
class couponserializers(serializers.ModelSerializer):

    class Meta :
        model = Coupon
        fields = '__all__'

class couponRequestserializers(serializers.ModelSerializer):

    class Meta :
        model = CouponRequest
        fields = '__all__'
        
class assignStaffCouponserializers(serializers.ModelSerializer):

    class Meta :
        model = AssignStaffCoupon
        fields = '__all__'

class assigncustomerCouponserializers(serializers.ModelSerializer):

    class Meta :
        model = AssignStaffCouponDetails
        fields = '__all__'
        
class couponStockSerializers(serializers.ModelSerializer):
    book_no = serializers.SerializerMethodField()

    class Meta :
        model = CouponStock
        fields = ['couponstock_id','book_no']
        
    def get_book_no(self,obj):
        return obj.couponbook.book_num