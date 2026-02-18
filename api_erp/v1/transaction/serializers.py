import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

from master.models import *
from accounts.models import *
from client_management.models import *
from van_management.models import *
from sales_management.models import *

    
class SalesReportSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    customer_code = serializers.CharField(source='customer.custom_id', read_only=True)
    total_supply_qty = serializers.IntegerField(source='get_total_supply_qty', read_only=True)
    net_taxable = serializers.SerializerMethodField()  
    amount_received = serializers.SerializerMethodField()  
    amount_total = serializers.SerializerMethodField()  
    invoice_type = serializers.SerializerMethodField() 
    quantity = serializers.SerializerMethodField()  
    price = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSupply
        fields = ['created_date', 'invoice_no', 'reference_number', 'customer_name', 'customer_code', 'amount_total', 'vat', 'discount', 'net_taxable', 'amount_received', 'total_supply_qty', 'invoice_type', 'quantity', 'price','status']

    def get_net_taxable(self, obj):
        return obj.net_payable

    def get_amount_received(self, obj):
        return obj.amount_recieved

    def get_amount_total(self, obj):
        return obj.subtotal
    
    def get_invoice_type(self, obj):
        if obj.amount_recieved > 0 or obj.customer.sales_type == "FOC":
            return "cash_invoice"
        elif obj.amount_recieved <= 0 and obj.customer.sales_type != "FOC":
            return "credit_invoice"
        return "all"
    
    def get_quantity(self, obj):
        return obj.get_total_supply_qty()  

    def get_price(self, obj):
        return obj.get_rate()
    
    def get_status(self, obj):
        return "Paid" if obj.amount_recieved >= obj.grand_total else "Pending"
    

class CustomerTransactionSerializer(serializers.ModelSerializer):
    
    date = serializers.SerializerMethodField()
    ref_invoice_no = serializers.CharField(source='customer_supply.reference_number', read_only=True)
    invoice_number = serializers.CharField(source='customer_supply.invoice_no', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    sales_type = serializers.CharField(source='customer_supply.customer.sales_type', read_only=True)
    qty = serializers.IntegerField(source='quantity', read_only=True)
    amount = serializers.DecimalField(source='customer_supply.grand_total', max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(source='customer_supply.discount', max_digits=10, decimal_places=2, read_only=True)
    net_taxable = serializers.DecimalField(source='customer_supply.subtotal', max_digits=10, decimal_places=2, read_only=True)
    vat_amount = serializers.DecimalField(source='customer_supply.vat', max_digits=10, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(source='customer_supply.grand_total', max_digits=10, decimal_places=2, read_only=True)
    amount_collected = serializers.DecimalField(source='customer_supply.amount_recieved', max_digits=10, decimal_places=2, read_only=True)

    salesman = serializers.CharField(source='customer_supply.salesman.username', read_only=True)
    emp_id = serializers.IntegerField(source='customer_supply.salesman.id', read_only=True)
    van = serializers.SerializerMethodField()
    location = serializers.CharField(source='customer_supply.customer.location', read_only=True)
    receipt_no = serializers.SerializerMethodField()
    receipt_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    emirate_name = serializers.CharField(source="customer_supply.customer.emirate.name", read_only=True)
    branch_name = serializers.CharField(source="customer_supply.customer.branch_id.name", read_only=True)
    route = serializers.CharField(source="customer_supply.customer.routes.route_name", read_only=True)

    class Meta:
        model = CustomerSupplyItems
        fields = [
            'id','date', 'ref_invoice_no', 'invoice_number', 'product_name', 'sales_type', 'qty', 'amount', 'discount', 
            'net_taxable', 'vat_amount', 'grand_total', 'amount_collected', 'salesman','emp_id', 'van', 'location', 
            'receipt_no', 'receipt_date', 'status', 'emirate_name', 'branch_name', 'route'
        ]

    def get_date(self, obj):
        return obj.customer_supply.created_date.date() if obj.customer_supply.created_date else None

    def get_van(self, obj):
        if obj.customer_supply.salesman and obj.customer_supply.salesman.salesman_van.exists():
            return obj.customer_supply.salesman.salesman_van.first().van_make
        return None

    def get_receipt_no(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.customer_supply.invoice_no).first()
        return receipt.receipt_number if receipt else None

    def get_receipt_date(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.customer_supply.invoice_no).first()
        return receipt.created_date.date() if receipt else None

    def get_status(self, obj):
        return "Paid" if obj.customer_supply.amount_recieved >= obj.customer_supply.grand_total else "Pending"
    
    
class CustomerCouponSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    ref_invoice_no = serializers.CharField(source='customer_coupon.reference_number', read_only=True)
    invoice_number = serializers.CharField(source='customer_coupon.invoice_no', read_only=True)
    product_name = serializers.CharField(source='coupon.book_num', read_only=True)
    sales_type = serializers.CharField(source='customer_coupon.customer.sales_type', read_only=True)
    qty = serializers.IntegerField(default=1)
    amount = serializers.DecimalField(source='customer_coupon.grand_total', max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(source='customer_coupon.discount', max_digits=10, decimal_places=2, read_only=True)
    net_taxable = serializers.DecimalField(source='customer_coupon.net_amount', max_digits=10, decimal_places=2, read_only=True)
    vat_amount = serializers.DecimalField(default=0, max_digits=10, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(source='customer_coupon.grand_total', max_digits=10, decimal_places=2, read_only=True)
    amount_collected = serializers.DecimalField(source='customer_coupon.amount_recieved', max_digits=10, decimal_places=2, read_only=True)
    salesman = serializers.CharField(source='customer_coupon.salesman.username', read_only=True)
    emp_id = serializers.CharField(source='customer_coupon.salesman.id', read_only=True)
    van = serializers.SerializerMethodField()
    location = serializers.CharField(source='customer_coupon.customer.location', read_only=True)
    receipt_no = serializers.SerializerMethodField()
    receipt_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    emirate_name = serializers.CharField(source="customer_coupon.customer.emirate.name", read_only=True)
    branch_name = serializers.CharField(source="customer_coupon.customer.branch_id.name", read_only=True)
    route = serializers.CharField(source="customer_coupon.customer.routes.route_name", read_only=True)

    class Meta:
        model = CustomerCouponItems
        fields = [
            'id','date', 'ref_invoice_no', 'invoice_number', 'product_name', 'sales_type', 'qty', 'amount', 'discount', 
            'net_taxable', 'vat_amount', 'grand_total', 'amount_collected', 'salesman','emp_id', 'van', 'location', 
            'receipt_no', 'receipt_date', 'status', 'emirate_name', 'branch_name', 'route'
        ]

    def get_date(self, obj):
        return obj.customer_coupon.created_date.date() if obj.customer_coupon.created_date else None

    def get_van(self, obj):
        if obj.customer_coupon.salesman and obj.customer_coupon.salesman.salesman_van.exists():
            return obj.customer_coupon.salesman.salesman_van.first().van_make
        return None

    def get_receipt_no(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.customer_coupon.invoice_no).first()
        return receipt.receipt_number if receipt else None

    def get_receipt_date(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.customer_coupon.invoice_no).first()
        return receipt.created_date.date() if receipt else None

    def get_status(self, obj):
        return "Paid" if obj.customer_coupon.amount_recieved >= obj.customer_coupon.grand_total else "Pending"

    
class ExpenseSummarySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="route.branch_id.name", read_only=True)
    staff_id = serializers.CharField(source="van.salesman.id", read_only=True)
    expense_type = serializers.CharField(source="expence_type.name", read_only=True)
    
    class Meta:
        model = Expense
        fields = ["branch_name", "staff_id", "expense_date", "expense_type", "amount"]
        
        
class SalesSummarySerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    staff_id = serializers.SerializerMethodField()
    trx_date = serializers.SerializerMethodField()
    sales_amount = serializers.DecimalField(source='grand_total', max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    vat = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_received = serializers.DecimalField(source='amount_recieved', max_digits=10, decimal_places=2)
    collected_empty_bottle = serializers.IntegerField()
    reference_number = serializers.CharField()
    invoice_no = serializers.CharField()

    class Meta:
        model = CustomerSupply
        fields = ['branch_name', 'staff_id', 'trx_date', 'sales_amount', 'discount', 'vat', 'amount_received', 'collected_empty_bottle', 'reference_number', 'invoice_no']

    def get_branch_name(self, obj):
        return obj.salesman.branch_id.name if obj.salesman and hasattr(obj.salesman, 'branch_id') else None

    def get_staff_id(self, obj):
        return obj.salesman.id if obj.salesman else None
    
    def get_trx_date(self, obj):
        return obj.created_date.date() 
    
    
# class CustomerTransactionSerializer(serializers.ModelSerializer):
    
#     date = serializers.SerializerMethodField()
#     ref_invoice_no = serializers.CharField(source='customer_supply.reference_number', read_only=True)
#     invoice_number = serializers.CharField(source='customer_supply.invoice_no', read_only=True)
#     product_name = serializers.CharField(source='product.product_name', read_only=True)
#     sales_type = serializers.CharField(source='customer_supply.customer.sales_type', read_only=True)
#     qty = serializers.IntegerField(source='quantity', read_only=True)
#     amount = serializers.DecimalField(source='customer_supply.grand_total', max_digits=10, decimal_places=2, read_only=True)
#     discount = serializers.DecimalField(source='customer_supply.discount', max_digits=10, decimal_places=2, read_only=True)
#     net_taxable = serializers.DecimalField(source='customer_supply.subtotal', max_digits=10, decimal_places=2, read_only=True)
#     vat_amount = serializers.DecimalField(source='customer_supply.vat', max_digits=10, decimal_places=2, read_only=True)
#     grand_total = serializers.DecimalField(source='customer_supply.grand_total', max_digits=10, decimal_places=2, read_only=True)
#     amount_collected = serializers.DecimalField(source='customer_supply.amount_recieved', max_digits=10, decimal_places=2, read_only=True)

#     salesman = serializers.CharField(source='customer_supply.salesman.username', read_only=True)
#     emp_id = serializers.IntegerField(source='customer_supply.salesman.id', read_only=True)
#     van = serializers.SerializerMethodField()
#     location = serializers.CharField(source='customer_supply.customer.location', read_only=True)
#     receipt_no = serializers.SerializerMethodField()
#     receipt_date = serializers.SerializerMethodField()
#     status = serializers.SerializerMethodField()
    
#     emirate_name = serializers.CharField(source="customer_supply.customer.emirate.name", read_only=True)
#     branch_name = serializers.CharField(source="customer_supply.customer.branch_id.name", read_only=True)
#     route = serializers.CharField(source="customer_supply.customer.routes.route_name", read_only=True)

#     class Meta:
#         model = CustomerSupplyItems
#         fields = [
#             'id','date', 'ref_invoice_no', 'invoice_number', 'product_name', 'sales_type', 'qty', 'amount', 'discount', 
#             'net_taxable', 'vat_amount', 'grand_total', 'amount_collected', 'salesman','emp_id', 'van', 'location', 
#             'receipt_no', 'receipt_date', 'status', 'emirate_name', 'branch_name', 'route'
#         ]

#     def get_date(self, obj):
#         return obj.customer_supply.created_date.date() if obj.customer_supply.created_date else None

#     def get_van(self, obj):
#         if obj.customer_supply.salesman and obj.customer_supply.salesman.salesman_van.exists():
#             return obj.customer_supply.salesman.salesman_van.first().van_make
#         return None

#     def get_receipt_no(self, obj):
#         receipt = Receipt.objects.filter(invoice_number=obj.customer_supply.invoice_no).first()
#         return receipt.receipt_number if receipt else None

#     def get_receipt_date(self, obj):
#         receipt = Receipt.objects.filter(invoice_number=obj.customer_supply.invoice_no).first()
#         return receipt.created_date.date() if receipt else None

#     def get_status(self, obj):
#         return "Paid" if obj.customer_supply.amount_recieved >= obj.customer_supply.grand_total else "Pending"
    
    
# class CustomerCouponSerializer(serializers.ModelSerializer):
#     date = serializers.SerializerMethodField()
#     ref_invoice_no = serializers.CharField(source='customer_coupon.reference_number', read_only=True)
#     invoice_number = serializers.CharField(source='customer_coupon.invoice_no', read_only=True)
#     product_name = serializers.CharField(source='coupon.book_num', read_only=True)
#     sales_type = serializers.CharField(source='customer_coupon.customer.sales_type', read_only=True)
#     qty = serializers.IntegerField(default=1)
#     amount = serializers.DecimalField(source='customer_coupon.grand_total', max_digits=10, decimal_places=2, read_only=True)
#     discount = serializers.DecimalField(source='customer_coupon.discount', max_digits=10, decimal_places=2, read_only=True)
#     net_taxable = serializers.DecimalField(source='customer_coupon.net_amount', max_digits=10, decimal_places=2, read_only=True)
#     vat_amount = serializers.DecimalField(default=0, max_digits=10, decimal_places=2, read_only=True)
#     grand_total = serializers.DecimalField(source='customer_coupon.grand_total', max_digits=10, decimal_places=2, read_only=True)
#     amount_collected = serializers.DecimalField(source='customer_coupon.amount_recieved', max_digits=10, decimal_places=2, read_only=True)
#     salesman = serializers.CharField(source='customer_coupon.salesman.username', read_only=True)
#     emp_id = serializers.CharField(source='customer_coupon.salesman.id', read_only=True)
#     van = serializers.SerializerMethodField()
#     location = serializers.CharField(source='customer_coupon.customer.location', read_only=True)
#     receipt_no = serializers.SerializerMethodField()
#     receipt_date = serializers.SerializerMethodField()
#     status = serializers.SerializerMethodField()

#     class Meta:
#         model = CustomerCouponItems
#         fields = [
#             'id','date', 'ref_invoice_no', 'invoice_number', 'product_name', 'sales_type', 'qty', 'amount', 'discount', 
#             'net_taxable', 'vat_amount', 'grand_total', 'amount_collected', 'salesman','emp_id', 'van', 'location', 
#             'receipt_no', 'receipt_date', 'status'
#         ]

#     def get_date(self, obj):
#         return obj.customer_coupon.created_date.date() if obj.customer_coupon.created_date else None

#     def get_van(self, obj):
#         if obj.customer_coupon.salesman and obj.customer_coupon.salesman.salesman_van.exists():
#             return obj.customer_coupon.salesman.salesman_van.first().van_make
#         return None

#     def get_receipt_no(self, obj):
#         receipt = Receipt.objects.filter(invoice_number=obj.customer_coupon.invoice_no).first()
#         return receipt.receipt_number if receipt else None

#     def get_receipt_date(self, obj):
#         receipt = Receipt.objects.filter(invoice_number=obj.customer_coupon.invoice_no).first()
#         return receipt.created_date.date() if receipt else None

#     def get_status(self, obj):
#         return "Paid" if obj.customer_coupon.amount_recieved >= obj.customer_coupon.grand_total else "Pending"

# Supply serializer start
class TransactionCusomerSupplyItemsSerializer(serializers.ModelSerializer):
    ERP_SYS_ITEM_ID = serializers.SerializerMethodField()
    product_id = serializers.CharField(source="product.pk", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    unit = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    vat = serializers.CharField(source="product.tax.percentage", read_only=True)
    
    class Meta:
        model = CustomerSupplyItems
        fields = ["id",'ERP_SYS_ITEM_ID','product_id','product_name','quantity','amount','unit','rate','vat']
        
    def get_ERP_SYS_ITEM_ID(self, obj):
        return obj.product.get_erp_product_id()
    
    def get_unit(self, obj):
        return obj.product.get_unit_display()
    
    def get_rate(self, obj):
        try:
            if obj.quantity == 0:
                return Decimal("0.00")
            return obj.amount / obj.quantity
        except (InvalidOperation, ZeroDivisionError):
            return Decimal("0.00")

class TransactionCusomerSupplySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()
    ref_invoice_no = serializers.CharField(source='reference_number', read_only=True)
    invoice_number = serializers.CharField(source='invoice_no', read_only=True)
    # sales_type = serializers.CharField(source='customer.sales_type', read_only=True)
    sales_type = serializers.SerializerMethodField()
    custom_id = serializers.CharField(source="customer.custom_id", read_only=True)
    customer_id = serializers.CharField(source="customer.customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer.customer_name", read_only=True)
    vat_amount = serializers.DecimalField(source='vat', max_digits=10, decimal_places=2, read_only=True)
    net_taxable = serializers.DecimalField(source='net_payable', max_digits=10, decimal_places=2, read_only=True)
    amount_collected = serializers.DecimalField(source='amount_recieved', max_digits=10, decimal_places=2, read_only=True)
    emp_id = serializers.CharField(source="salesman.pk", read_only=True)
    emirate_id = serializers.CharField(source="customer.emirate.pk", read_only=True)
    emirate_name = serializers.CharField(source="customer.emirate.name", read_only=True)
    branch_name = serializers.CharField(source="salesman.branch_id.branch_name", read_only=True)
    branch_id = serializers.CharField(source="salesman.branch_id.pk", read_only=True)
    route = serializers.CharField(source="customer.routes.route_name", read_only=True)
    van_id = serializers.SerializerMethodField()
    van_plate = serializers.SerializerMethodField()
    location_id = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    receipt_no = serializers.SerializerMethodField()
    receipt_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    payment_type = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSupply
        fields = [
            "id",'date',"transaction_type", "customer_id", "custom_id", "customer_name",
            'discount','net_taxable','vat_amount','grand_total','amount_collected','payment_type',
            "ref_invoice_no","invoice_number","sales_type","emp_id","emirate_id","emirate_name",
            "branch_name","route","van_id","van_plate",'location_id','location_name','receipt_no','receipt_date','status','products','branch_name','branch_id'
            ]
    
    def get_date(self, obj):
        return localtime(obj.created_date).date()
    
    def get_van_id(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.pk if van else ""

    
    def get_van_plate(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.plate if van else ""
    
    def get_location_id(self,obj):
        try :
            return obj.customer.location.pk
        except:
            return ""
    
    def get_location_name(self,obj):
        try :
            return obj.customer.location.location_name
        except:
            return ""
    
    def get_transaction_type(self,obj):
        return "supply"
    
    def get_sales_type(self, obj):
        sales_type = obj.customer.sales_type

        if sales_type == "FOC":
            return "FOC"
        elif sales_type == "CASH COUPON":
            return "CASH COUPON"
        elif obj.amount_recieved == 0:
            return "CREDIT"
        else:
            return "CASH"
    
    def get_receipt_no(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.invoice_no).first()
        return receipt.receipt_number if receipt else None
    
    def get_receipt_date(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.invoice_no).first()
        return receipt.created_date.date() if receipt else None
    
    
    def get_products(self, obj):
        instances = CustomerSupplyItems.objects.filter(customer_supply=obj)
        serialized = TransactionCusomerSupplyItemsSerializer(instances, many=True)
        return serialized.data
    
    def get_payment_type(self, obj):
        return_value = ""

        if (obj.grand_total != 0 ) and (obj.grand_total == obj.amount_recieved) :
            return_value = "CASH"
        else:
            if obj.customer.sales_type == "CREDIT":
                return_value = "CREDIT"
            if obj.customer.sales_type == "CASH COUPON":
                return_value = "COUPON"
            if obj.customer.sales_type == "FOC":
                return_value = "FOC"
        return return_value
    
    def get_status(self, obj):
        if obj.amount_recieved >= obj.grand_total and obj.grand_total > 0:
            return "Paid"
        else:
            return "Unpaid"
# Supply serializer end


# Recharge serializer start
class TransactionCusomerCouponItemsSerializer(serializers.ModelSerializer):
    ERP_SYS_ITEM_ID = serializers.SerializerMethodField()
    product_id = serializers.CharField(source="coupon.pk", read_only=True)
    product_name = serializers.CharField(source="coupon.book_num", read_only=True)
    quantity = serializers.SerializerMethodField()
    # vat = serializers.CharField(source="product.tax.percentage", read_only=True)
    
    class Meta:
        model = CustomerCouponItems
        fields = ["id",'ERP_SYS_ITEM_ID','product_id','product_name','quantity','rate']
        
    def get_ERP_SYS_ITEM_ID(self, obj):
        return ""
    
    def get_quantity(self, obj):
        return 1

class TransactionCusomerCouponSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    
    date = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()
    
    ref_invoice_no = serializers.CharField(source='reference_number', read_only=True)
    invoice_number = serializers.CharField(source='invoice_no', read_only=True)
    
    sales_type = serializers.CharField(source='customer.sales_type', read_only=True)
    custom_id = serializers.CharField(source="customer.custom_id", read_only=True)
    customer_id = serializers.CharField(source="customer.customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer.customer_name", read_only=True)
    
    # vat_amount = serializers.DecimalField(source='vat', max_digits=10, decimal_places=2, read_only=True)
    net_taxable = serializers.DecimalField(source='net_payable', max_digits=10, decimal_places=2, read_only=True)
    amount_collected = serializers.DecimalField(source='amount_recieved', max_digits=10, decimal_places=2, read_only=True)
    
    emp_id = serializers.CharField(source="salesman.pk", read_only=True)
    emirate_id = serializers.CharField(source="customer.emirate.pk", read_only=True)
    emirate_name = serializers.CharField(source="customer.emirate.name", read_only=True)
    branch_name = serializers.CharField(source="salesman.branch_id.branch_name", read_only=True)
    branch_id = serializers.CharField(source="salesman.branch_id.pk", read_only=True)
    route = serializers.CharField(source="customer.routes.route_name", read_only=True)
    van_id = serializers.SerializerMethodField()
    van_plate = serializers.SerializerMethodField()
    location_id = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    # payment_mode = serializers.SerializerMethodField()
    
    receipt_no = serializers.SerializerMethodField()
    receipt_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    
    
    class Meta:
        model = CustomerCoupon
        fields = [
            "id",'date',"transaction_type", "customer_id", "custom_id", "customer_name",'payment_type',
            'discount','net_taxable','grand_total','amount_collected',
            "ref_invoice_no","invoice_number","sales_type","emp_id","emirate_id","emirate_name",
            "branch_id","branch_name","route","van_id","van_plate",'location_id','location_name','receipt_no','receipt_date','status','products'
            ]
    
    def get_date(self, obj):
        return localtime(obj.created_date).date()
    
    def get_van_id(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.pk if van else ""
    
    def get_van_plate(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.plate if van else ""
    
    def get_location_id(self,obj):
        try :
            return obj.customer.location.pk
        except:
            return ""
    
    def get_location_name(self,obj):
        try :
            return obj.customer.location.location_name
        except:
            return ""
    
    def get_transaction_type(self,obj):
        return "coupon_recharge"
    
    def get_receipt_no(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.invoice_no).first()
        return receipt.receipt_number if receipt else None
    
    def get_receipt_date(self, obj):
        receipt = Receipt.objects.filter(invoice_number=obj.invoice_no).first()
        return receipt.created_date.date() if receipt else None
    
    def get_status(self, obj):
        if obj.amount_recieved >= obj.grand_total:
            return "Paid"
        elif obj.amount_recieved == 0 or obj.amount_recieved <= obj.grand_total:
            return "Unpaid"
    
    def get_products(self, obj):
        instances = CustomerCouponItems.objects.filter(customer_coupon=obj)
        serialized = TransactionCusomerCouponItemsSerializer(instances, many=True)
        return serialized.data
    
    def get_payment_type(self, obj):
        return obj.get_payment_type_display()

# collection
class TransactionCollectionItemSerializer(serializers.ModelSerializer):
    invoice_id = serializers.CharField(source="invoice.pk", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_no", read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_received = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    invoice_status = serializers.CharField(source="invoice.invoice_status", read_only=True)
    
    class Meta:
        model = CollectionItems
        fields = ["invoice_id","invoice_number", "amount", "balance", "amount_received","invoice_status"]


class TransactionCollectionPaymentSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(source="customer.customer_id", read_only=True)
    custom_id = serializers.CharField(source="customer.custom_id", read_only=True)
    customer_name = serializers.CharField(source="customer.customer_name", read_only=True)
    collection_date = serializers.SerializerMethodField()
    amount_collected = serializers.DecimalField(source="amount_received", max_digits=10, decimal_places=2, read_only=True)
    receipt_number = serializers.CharField(read_only=True)
    # payment_method = serializers.CharField(read_only=True)
    payment_type = serializers.CharField(source="payment_method", read_only=True)
    salesman = serializers.CharField(source="salesman.username", read_only=True)
    emp_id = serializers.IntegerField(source="salesman.id", read_only=True)
    total_amount = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    total_net_taxable = serializers.SerializerMethodField()
    total_vat = serializers.SerializerMethodField()
    collected_amount = serializers.SerializerMethodField()
    is_repeated_customer = serializers.SerializerMethodField()
    invoices = serializers.SerializerMethodField()

    date = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()

    emirate_id = serializers.CharField(source="customer.emirate.pk", read_only=True)
    emirate_name = serializers.CharField(source="customer.emirate.name", read_only=True)
    branch_name = serializers.CharField(source="salesman.branch_id.branch_name", read_only=True)
    branch_id = serializers.CharField(source="salesman.branch_id.pk", read_only=True)
    route = serializers.CharField(source="customer.routes.route_name", read_only=True)
    location_id = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    van_id = serializers.SerializerMethodField()
    van_plate = serializers.SerializerMethodField()

    class Meta:
        model = CollectionPayment
        fields = [
            "id",'date',"transaction_type", "customer_id", "custom_id", "customer_name", "collection_date", "amount_collected",
            "receipt_number", "payment_type", "salesman","emp_id","emirate_id","emirate_name",
            "branch_id","branch_name","route","van_id","van_plate", "total_amount", "total_discount",'location_id','location_name',
            "total_net_taxable", "total_vat", "collected_amount", "is_repeated_customer", "invoices"
        ]
    
    def get_date(self, obj):
        return localtime(obj.created_date).date()
        
    def get_transaction_type(self,obj):
        return "collection" 

    def get_van_id(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.pk if van else ""
    
    def get_van_plate(self,obj):
        van = Van.objects.filter(salesman=obj.salesman).first()
        return van.plate if van else ""
    
    def get_location_id(self,obj):
        try :
            return obj.customer.location.pk
        except:
            return ""
    
    def get_location_name(self,obj):
        try :
            return obj.customer.location.location_name
        except:
            return ""

    def get_collection_date(self, obj):
        return obj.created_date.date() if obj.created_date else None

    def get_total_amount(self, obj):
        return obj.total_amount()

    def get_total_discount(self, obj):
        return obj.total_discounts()

    def get_total_net_taxable(self, obj):
        return obj.total_net_taxeble()

    def get_total_vat(self, obj):
        return obj.total_vat()

    def get_collected_amount(self, obj):
        return obj.collected_amount()

    def get_is_repeated_customer(self, obj):
        return obj.is_repeated_customer()
    
    def get_invoices(self, obj):
        instances = CollectionItems.objects.filter(collection_payment=obj)
        serialized = TransactionCollectionItemSerializer(instances, many=True)
        return serialized.data
    
    
    
class StaffOrderDetailsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name', read_only=True)

    class Meta:
        model = Staff_Orders_details
        fields = ['staff_order_details_id', 'product_name', 'count', 'issued_qty']


class StaffIssueOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name', read_only=True)
    route_name = serializers.CharField(source='van_route_id.route_name', read_only=True)
    salesman_name = serializers.CharField(source='salesman_id.get_full_name', read_only=True)
    details = StaffOrderDetailsSerializer(source='staff_Orders_details_id', read_only=True)

    class Meta:
        model = Staff_IssueOrders
        fields = [
            'order_number', 'salesman_name', 'product_name',
            'quantity_issued', 'stock_quantity', 'status',
            'route_name', 'modified_date', 'details'
        ]


class VanIssueDataSerializer(serializers.Serializer):
    van_id = serializers.UUIDField()
    van_name = serializers.CharField()
    van_plate = serializers.CharField()
    issued_orders = StaffIssueOrderSerializer(many=True)
    
    
class AuditDetailsSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)

    class Meta:
        model = AuditDetails
        fields = [
            'id',
            'customer',
            'customer_name',
            'previous_outstanding_amount',
            'outstanding_amount',
            'previous_bottle_outstanding',
            'bottle_outstanding',
            'previous_outstanding_coupon',
            'outstanding_coupon',
            'get_amount_variation',
            'get_bottle_variation',
            'get_coupon_variation'
        ]
        read_only_fields = [
            'get_amount_variation',
            'get_bottle_variation',
            'get_coupon_variation'
        ]

class AuditBaseSerializer(serializers.ModelSerializer):
    audit_details = AuditDetailsSerializer(many=True, required=False)
    route_name = serializers.CharField(source='route.route_name', read_only=True)
    marketing_name = serializers.CharField(source='marketing_executieve.name', read_only=True)

    class Meta:
        model = AuditBase
        fields = [
            'id',
            'created_by', 'created_date', 'modified_by', 'modified_date',
            'start_date', 'end_date',
            'route', 'route_name',
            'marketing_executieve', 'marketing_name',
            'salesman', 'helper', 'driver',
            'audit_details'
        ]