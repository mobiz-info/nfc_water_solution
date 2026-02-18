from django import forms
from django.forms import ModelForm
from .models import *
from master.models import *


class Products_Create_Form(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['product_name','quantity']
        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'})

        }
class Product_Item_Create_Form(forms.ModelForm):
    class Meta:
        model = ProdutItemMaster
        fields = ['product_name','category','unit','rate','tax','image']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'unit': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'rate': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'tax' : forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class Products_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        model = Product
        fields = ['product_name']
        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Defaultprice_Create_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        model = Product_Default_Price_Level
        fields = ['product_id', 'customer_type', 'rate']
        widgets = {
            'product_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'rate': forms.TextInput(attrs={'class': 'form-control'})
        }


class Defaultprice_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Product_Default_Price_Level
        fields = ['customer_type', 'rate']
        widgets = {
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'rate' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'})
        }

class StaffIssueOrdersForm(forms.ModelForm):
    class Meta:
        model = Staff_IssueOrders
        # fields = ['order_number', 'salesman_id', 'staff_Orders_details_id', 'van_route_id', 'product_id', 'quantity_issued', 'status']
        fields = ['quantity_issued']

        widgets = {
            # 'order_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            # 'salesman_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            # 'staff_Orders_details_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            # 'van_route_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            # 'product_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'quantity_issued': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            # 'status': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
        }
class StaffIssue_CouponsOrdersForm(forms.ModelForm):
    coupo_no = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon no', 'readonly': 'readonly'}))
    
    class Meta:
        model = Staff_IssueOrders
        fields = ['quantity_issued',]

        widgets = {
            # 'salesman_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            # 'van_route_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'quantity_issued': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }
        
class StockTransferForm(forms.Form):
    product_id = forms.ModelChoiceField(
        queryset=ProdutItemMaster.objects.all(),
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'false'})
    )
    used_quantity = forms.IntegerField(
        min_value=0,
        required=False,
        label="Used Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'false'})
    )
    damage_quantity = forms.IntegerField(
        min_value=0,
        required=False,
        label="Damage Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'false'})
    )
    
class ScrapStockForm(forms.Form):
    product = forms.ModelChoiceField(queryset=ProdutItemMaster.objects.all(), label="Product")
    cleared_quantity = forms.IntegerField(label="Cleared Quantity")
    
    
class ProductionDamageReasonForm(forms.ModelForm):
    
    class Meta:
        model = ProductionDamageReason
        fields = ['reason']
        
        widgets = {
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductionDamageForm(forms.ModelForm):
    
    class Meta:
        model = ProductionDamage
        fields = ['route','reason','product_from','product_to','quantity']
        
        widgets = {
            'route': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'product_from': forms.Select(attrs={'class': 'form-control'}),
            'product_to': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class WashedUsedProductForm(forms.ModelForm):
    class Meta:
        model = WashedUsedProduct
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}),
        }