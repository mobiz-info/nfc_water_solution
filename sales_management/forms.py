# forms.py
from django import forms
from django.db.models import Q
from master.models import RouteMaster  # Assuming you have imported RouteMaster
from accounts.models import Customers
from invoice_management.models import SuspenseCollection
from django.forms import TextInput
from van_management.models import VanProductStock,BottleCount
from accounts.models import *
from sales_management.models import *

class SaleEntryFilterForm(forms.Form):
    route_name = forms.ModelChoiceField(
        queryset=RouteMaster.objects.all(),
        empty_label="All Routes",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
    )

    # search_query = forms.CharField(
    #     label='Search',
    #     max_length=100,
    #     required=False,
    #     widget=forms.TextInput(attrs={'class': 'form-control'})
    # )


from django import forms
from product.models import Product
from master.models import CategoryMaster


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=CategoryMaster.objects.all(),
        label='Category',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product_name = forms.ModelChoiceField(
        queryset=Product.objects.none(), 
        label='Product',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    coupon_method = forms.BooleanField(
        label='Select Coupon', 
        required=False, 
        widget=forms.RadioSelect(choices=[('digital', 'Digital'), ('manual', 'Manual')])
    )

    class Meta:
        model = Product
        fields = ['product_name', 'coupon_method']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if 'category' in self.data:
    #         try:
    #             category_id = int(self.data.get('category'))
    #             self.fields['product_name'].queryset = Product.objects.filter(product_name__category__pk=category_id).order_by('product_name')
    #         except (ValueError, TypeError):
    #             pass
    #     else:
    #         self.fields['product_name'].queryset = Product.objects.none()

        # # Set default value for coupon_method
        # self.fields['coupon_method'].initial = 'manual'



from django import forms
from .models import SalesExtraModel



class CashCustomerSaleForm(forms.ModelForm):
    status = forms.ChoiceField(choices=SalesExtraModel.STATUS_CHOICES, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(CashCustomerSaleForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Set required attribute to False for all fields
            field.required = False

        # Prepopulate bottle_variations field
        empty_bottles = self.instance.empty_bottles if self.instance else None
        collected_bottles = self.instance.collected_bottles if self.instance else None
        self.fields['bottle_variations'].initial = max(0, empty_bottles - collected_bottles) if empty_bottles is not None and collected_bottles is not None else 0

    class Meta:
        model = SalesExtraModel
        fields = ['qty_needed', 'empty_bottles', 'collected_bottles', 'bottle_variations']


class CreditCustomerSaleForm(forms.ModelForm):
    status = forms.ChoiceField(choices=SalesExtraModel.STATUS_CHOICES, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(CreditCustomerSaleForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        # Prepopulate bottle_variations field
        empty_bottles = self.instance.empty_bottles if self.instance else None
        collected_bottles = self.instance.collected_bottles if self.instance else None
        self.fields['bottle_variations'].initial = max(0, empty_bottles - collected_bottles) if empty_bottles is not None and collected_bottles is not None else 0

    class Meta:
        model = SalesExtraModel
        fields = ['qty_needed', 'empty_bottles', 'collected_bottles', 'bottle_variations']

class CashCouponCustomerSaleForm(forms.ModelForm):
    status = forms.ChoiceField(choices=SalesExtraModel.STATUS_CHOICES, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(CashCouponCustomerSaleForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        # Prepopulate bottle_variations field
        empty_bottles = self.instance.empty_bottles if self.instance else None
        collected_bottles = self.instance.collected_bottles if self.instance else None
        self.fields['bottle_variations'].initial = max(0, empty_bottles - collected_bottles) if empty_bottles is not None and collected_bottles is not None else 0

    class Meta:
        model = SalesExtraModel
        fields = ['qty_needed', 'no_of_coupons', 'empty_bottles', 'collected_bottles', 'bottle_variations']

class CreditCouponCustomerSaleForm(forms.ModelForm):
    status = forms.ChoiceField(choices=SalesExtraModel.STATUS_CHOICES, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(CreditCouponCustomerSaleForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        # Prepopulate bottle_variations field
        empty_bottles = self.instance.empty_bottles if self.instance else None
        collected_bottles = self.instance.collected_bottles if self.instance else None
        self.fields['bottle_variations'].initial = max(0, empty_bottles - collected_bottles) if empty_bottles is not None and collected_bottles is not None else 0

    class Meta:
        model = SalesExtraModel
        fields = ['qty_needed', 'no_of_coupons', 'coupon_variations', 'empty_bottles', 'collected_bottles', 'bottle_variations']

class SuspenseCollectionForm(forms.ModelForm):
    payable_amount = forms.DecimalField(label='Payable Amount', required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payable Amount', 'readonly': 'readonly'}))
    
    class Meta:
        model = SuspenseCollection
        fields = ['amount_paid', 'reference_no']

        widgets = {
            'amount_paid': TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'Amount to be Paid'}), 
            'reference_no': TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference No'}), 
        }


class VansRouteBottleCountAddForm(forms.ModelForm):
    qty_added = forms.IntegerField(min_value=0, label='Qty Added', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = BottleCount
        fields = ['qty_added']
        # widgets = {
        #     'comment': forms.TextInput(attrs={'class': 'form-control'}),
        # }
    
    # def save(self, commit=True, *args, **kwargs):
    #     bottle_count = super().save(commit=False, *args, **kwargs)
    #     bottle_count.created_by = self.request.user.username  # Assuming request.user is available
    #     if commit:
    #         bottle_count.save()

    #         # Update VanProductStock if exists
    #         van_product_stock = VanProductStock.objects.filter(van=bottle_count.van, created_date=bottle_count.created_date.date()).first()
    #         if van_product_stock:
    #             van_product_stock.stock += self.cleaned_data['qty_added']
    #             van_product_stock.save()

    #     return bottle_count



class VansRouteBottleCountDeductForm(forms.ModelForm):
    qty_deducted = forms.IntegerField(min_value=0, label='Qty Deducted', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = BottleCount
        fields = ['qty_deducted']
        # widgets = {
        #     'comment': forms.TextInput(attrs={'class': 'form-control'}),
        # }

    # def save(self, commit=True, *args, **kwargs):
    #     bottle_count = super().save(commit=False, *args, **kwargs)
    #     bottle_count.created_by = self.request.user.username  # Assuming request.user is available
    #     if commit:
    #         bottle_count.save()

    #         # Update VanProductStock if exists
    #         van_product_stock = VanProductStock.objects.filter(van=bottle_count.van, created_date=bottle_count.created_date.date()).first()
    #         if van_product_stock:
    #             van_product_stock.stock -= self.cleaned_data['qty_deducted']
    #             van_product_stock.save()

    #     return bottle_count
    
    
class CashCollectionForm(forms.ModelForm):
    class Meta:
        model = CollectionPayment
        fields = ['amount_received']
        
class ChequeCollectionForm(forms.ModelForm):
    class Meta:
        model = CollectionCheque
        fields = ['bank_name', 'cheque_amount',  'cheque_no']
        
        
class InvoicePaymentForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_no', 'amout_recieved']

    # invoice_id = forms.UUIDField(widget=forms.HiddenInput())
    # amount_received = forms.DecimalField(max_digits=10, decimal_places=2, required=True)