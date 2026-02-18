from django import forms
from django.forms import ModelForm

from sales_management.models import CollectionPayment
from van_management.models import *
from .models import *
from accounts.models import Customers
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils import timezone

        
class Vacation_Add_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['customer'].queryset = Customers.objects.all()
        
    class Meta:
        model = Vacation
        fields = ['customer', 'start_date','end_date','note']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date', 'min':timezone.now().date()}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date', 'min':timezone.now().date()}),
            'note' : forms.TextInput(attrs={'class':'form-control'})
        }

class Vacation_Edit_Form(forms.ModelForm):
    class Meta:
        model = Vacation
        fields = [ 'start_date', 'end_date', 'note']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date', 'min':timezone.now().date()}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date', 'min':timezone.now().date()}),
            'note': forms.TextInput(attrs={'class': 'form-control'})
        }

class CustomerSearchForm(forms.Form):
    search_query = forms.CharField(label='Search')

from master.models import RouteMaster

class CustodyItemFilterForm(forms.Form):
    route_name = forms.ModelChoiceField(
        queryset=RouteMaster.objects.all(),
        empty_label="All Routes",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
    )


# from django import forms
# from product.models import Product
# from master.models import CategoryMaster
# from django import forms
# from .models import CustodyCustomItems
# class CustomerCustodyItemsForm(forms.ModelForm):
#     class Meta:
#         model = CustodyCustomItems
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'


# class CustomerCustodyItemsForm(forms.ModelForm):
#     DEPOSIT_TYPES = [
#         ('deposit', 'Deposit'),
#         ('non_deposit', 'Non-Deposit'),
#     ]

#     deposit_type = forms.ChoiceField(
#         choices=DEPOSIT_TYPES,
#         widget=forms.RadioSelect(),
#         label='Deposit Type'
#     )
#     class Meta:
#         model = CustodyCustomItems
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'

#         # Limit the queryset for the product field to only 5 gallon, dispenser, and coolers
#         self.fields['product'].queryset = Product.objects.filter(
#             product_name__in=["5 Gallon", "Water Cooler", "Dispenser"]
        # )




# class CustodyCustomItemsForm(forms.ModelForm):
#     DEPOSIT_TYPES = [
#         ('deposit', 'Deposit'),
#         ('non_deposit', 'Non-Deposit'),
#     ]

#     deposit_type = forms.ChoiceField(
#         choices=DEPOSIT_TYPES,
#         widget=forms.RadioSelect(),
#         label='Deposit Type'
#     )

#     class Meta:
#         model = CustodyCustomItems
#         fields = ['product', 'count', 'serialnumber', 'deposit_type']
#         widgets = {
#             'deposit_type': forms.RadioSelect()
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['amount'] = forms.IntegerField(label='Amount', required=False)
#         self.fields['deposit_form_number'] = forms.CharField(max_length=100, label='Deposit Form Number', required=False)

#         # Hide amount and deposit_form_number fields by default
#         self.fields['amount'].widget = forms.HiddenInput()
#         self.fields['deposit_form_number'].widget = forms.HiddenInput()

#         # Show amount and deposit_form_number fields if deposit_type is 'deposit'
#         if self.instance.deposit_type == 'deposit':
#             self.fields['amount'].widget = forms.NumberInput()
#             self.fields['deposit_form_number'].widget = forms.TextInput()

#     def clean(self):
#         cleaned_data = super().clean()
#         deposit_type = cleaned_data.get('deposit_type')

#         # Validate amount and deposit_form_number fields if deposit_type is 'deposit'
#         if deposit_type == 'deposit':
#             amount = cleaned_data.get('amount')
#             deposit_form_number = cleaned_data.get('deposit_form_number')

#             if not amount:
#                 self.add_error('amount', 'Amount is required for deposit type.')
#             if not deposit_form_number:
#                 self.add_error('deposit_form_number', 'Deposit form number is required for deposit type.')

# #         return cleaned_data


# class CustodyCustomItemsForm(forms.ModelForm):
#     DEPOSIT_TYPES = [
#         ('deposit', 'Deposit'),
#         ('non_deposit', 'Non-Deposit'),
#     ]

#     deposit_type = forms.ChoiceField(
#         choices=DEPOSIT_TYPES,
#         widget=forms.RadioSelect(),
#         label='Deposit Type'
#     )

#     class Meta:
#         model = CustodyCustomItems
#         fields = ['product', 'count', 'serialnumber', 'deposit_type']
#         widgets = {
#             'deposit_type': forms.RadioSelect()
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['amount'] = forms.IntegerField(label='Amount', required=False)
#         self.fields['deposit_form_number'] = forms.CharField(max_length=100, label='Deposit Form Number', required=False)

#         # Hide amount and deposit_form_number fields by default
#         self.fields['amount'].widget = forms.HiddenInput()
#         self.fields['deposit_form_number'].widget = forms.HiddenInput()

#         # Show amount and deposit_form_number fields if deposit_type is 'deposit'
#         if self.instance.deposit_type == 'deposit':
#             self.fields['amount'].widget = forms.NumberInput()
#             self.fields['deposit_form_number'].widget = forms.TextInput()

#     def clean(self):
#         cleaned_data = super().clean()
#         deposit_type = cleaned_data.get('deposit_type')

#         # Validate amount and deposit_form_number fields if deposit_type is 'deposit'
#         if deposit_type == 'deposit':
#             amount = cleaned_data.get('amount')
#             deposit_form_number = cleaned_data.get('deposit_form_number')

#             if not amount:
#                 self.add_error('amount', 'Amount is required for deposit type.')
#             if not deposit_form_number:
#                 self.add_error('deposit_form_number', 'Deposit form number is required for deposit type.')

#         return cleaned_data
    
from master.models import RouteMaster

class CustodyItemFilterForm(forms.Form):
    route_name = forms.ModelChoiceField(
        queryset=RouteMaster.objects.all(),
        empty_label="All Routes",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
    )

from django import forms
from product.models import Product
from master.models import CategoryMaster
from django import forms
from .models import *
# class CustomerCustodyItemsForm(forms.ModelForm):
    
#     class Meta:
#         model = CustodyCustomItems
#         fields = ['customer', 'product', 'count', 'deposit_form', 'deposit_form_number','serialnumber','amount']
#         widgets = {

#         'customer': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
#         'product': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
#         'count': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
#         'amount': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
#         'deposit_form': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
#         'serialnumber': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
#         'deposit_form_number': forms.TextInput(attrs={'class': 'form-control', 'type': 'hidden', 'required': 'true'}),
#         }

   
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filter the queryset of the product field to include only specific products
#         product_choices = Product.objects.filter(product_name__in=["5 Gallon", "Water Cooler", "Dispenser"])
#         self.fields['product'].queryset = product_choices

# class CustodyCustomItemsForm(forms.Form):
#     from_date = forms.DateField(label='From Date', widget=forms.DateInput(attrs={'type': 'date'}))
#     to_date = forms.DateField(label='To Date', widget=forms.DateInput(attrs={'type': 'date'}))



# class CustodyCustomItemForm(forms.ModelForm):
#     class Meta:
#         model = CustodyCustomItems
#         fields = ['product', 'count', 'serialnumber','deposit_form','deposit_form_number','amount']
#         widgets = {
#             'product': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
#             'count': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
#             'serialnumber': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
           
#         }

class CustodyCustomForm(forms.ModelForm):
    
    amount_collected = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = CustodyCustom
        fields = ['agreement_no','total_amount','deposit_type','amount_collected']
        
        widgets = {
            'agreement_no': forms.TextInput(attrs={'class': 'form-control'}),
            'total_amount': forms.TextInput(attrs={'class': 'form-control'}),
            'deposit_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'amount_collected': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustodyCustomItemForm(forms.ModelForm):

    class Meta:
        model = CustodyCustomItems
        fields = ['product', 'quantity', 'serialnumber', 'amount']
        
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'required': True,}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter QTY'}),
            'serialnumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Serial Number'}),
            'amount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'}),
        }


#------------------- Customer Supply------------------
class CustomerSupplyForm(forms.ModelForm):
    
    adding_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'id': 'adding_date_field'})
    )
    
    class Meta:
        model = CustomerSupply
        fields = ['adding_date','grand_total','discount','net_payable','vat','subtotal','amount_recieved','collected_empty_bottle','allocate_bottle_to_free','allocate_bottle_to_custody','allocate_bottle_to_paid','reference_number']

        widgets = {
            # 'created_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date-input'}),
            'grand_total': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Grand Total'}),
            'discount': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Discount'}),
            'net_payable': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Net Payable'}),
            'vat': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter VAT'}),
            'subtotal': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Sub Total'}),
            'amount_recieved': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Amount Recieved'}),
            'collected_empty_bottle': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Collected Empty Bottle'}),
            'allocate_bottle_to_free': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Pending'}),
            'allocate_bottle_to_custody': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Custody'}),
            'allocate_bottle_to_paid': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Paid'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Reference No.'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adding_date'].initial = date.today()
        
class EditCustomerSupplyForm(forms.ModelForm):

    class Meta:
        model = CustomerSupply
        fields = ['grand_total','discount','net_payable','vat','subtotal','amount_recieved','collected_empty_bottle','allocate_bottle_to_free','allocate_bottle_to_custody','allocate_bottle_to_paid','reference_number']

        widgets = {
            'grand_total': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Grand Total'}),
            'discount': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Discount'}),
            'net_payable': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Net Payable'}),
            'vat': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter VAT'}),
            'subtotal': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Sub Total'}),
            'amount_recieved': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Amount Recieved'}),
            'collected_empty_bottle': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Collected Empty Bottle'}),
            'allocate_bottle_to_free': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Pending'}),
            'allocate_bottle_to_custody': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Custody'}),
            'allocate_bottle_to_paid': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Enter Allocated to Bottle Paid'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'required': False, 'placeholder': 'Enter Reference No.'}),
        }

class CustomerSupplyItemsForm(forms.ModelForm):

    class Meta:
        model = CustomerSupplyItems
        fields = ['product','quantity','amount']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control'}),
        }
#
class CoupenEditForm(forms.ModelForm):
    class Meta:
        model = CustomerCouponStock
        fields = ['coupon_type_id', 'count']  # Include the 'coupon_type_id' field
        widgets = {
            'count': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'coupon_type_id': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }

    def clean_count(self):
        count = self.cleaned_data['count']
        if count <= 0:
            raise forms.ValidationError("Count must be a positive integer.")
        return count

    def save(self, commit=True):
        instance = super(CoupenEditForm, self).save(commit=False)
        instance.count = self.cleaned_data['count']
        if commit:
            instance.save()
        return instance
    
class CustomerOutstandingForm(forms.ModelForm):

    class Meta:
        model = CustomerOutstanding
        fields = ['customer','product_type', 'created_date']

        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2', 'data-live-searc':'true'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'created_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
class CustomerOutstandingSingleForm(forms.ModelForm):

    class Meta:
        model = CustomerOutstanding
        fields = ['product_type', 'created_date']

        widgets = {
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'created_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
class CustomerOutstandingAmountForm(forms.ModelForm):

    class Meta:
        model = OutstandingAmount
        fields = ['amount']

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class CustomerOutstandingBottleForm(forms.ModelForm):

    class Meta:
        model = OutstandingProduct
        fields = ['empty_bottle']

        widgets = {
            'empty_bottle': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class CustomerOutstandingCouponsForm(forms.ModelForm):

    class Meta:
        model = OutstandingCoupon
        fields = ['coupon_type','count']

        widgets = {
            'coupon_type': forms.Select(attrs={'class': 'form-control'}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CustomerOrdersAcknowledgeForm(forms.ModelForm):
    class Meta:
        model = CustomerOrders
        fields = ['order_status']
        
        widgets = {
            'order_status': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
class Create_NonVisitReasonForm(forms.ModelForm):
    class Meta:
        model = NonVisitReason
        fields = ['reason_text']
        widgets = {
            'reason_text': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter reason text here'}),
        }
        
        
class UploadOutstandingForm(forms.Form):
    route = forms.ModelChoiceField(queryset=RouteMaster.objects.all(),label="Select Route",required=True,
            widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Route'
        })
    )
    excel_file = forms.FileField(label="Upload Excel File",required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Upload File'
        })
    )
    
class EligibleCustomerConditionsForm(forms.ModelForm):

    class Meta:
        model = EligibleCustomerConditions
        fields = ['category_name','moq','days']

        widgets = {
            'category_name': forms.Select(attrs={'class': 'form-control'}),
            'moq': forms.NumberInput(attrs={'class': 'form-control'}),
            'days': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        
class AuditDetailsForm(forms.ModelForm):
    class Meta:
        model = AuditDetails
        fields = ['outstanding_amount', 'bottle_outstanding', 'outstanding_coupon']
        
        widgets = {
                'outstanding_amount': forms.NumberInput(attrs={'class': 'form-control'}),
                'bottle_outstanding': forms.NumberInput(attrs={'class': 'form-control'}),
                'outstanding_coupon': forms.NumberInput(attrs={'class': 'form-control'}),
            }

class CustodyItemReturnForm(forms.ModelForm):
    class Meta:
        model = CustomerReturnItems
        fields = ['quantity', 'amount', 'serialnumber']
        labels = {
            'quantity': 'Quantity',
            'amount': 'Total Amount',
            'serialnumber': 'Serial Number',
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'serialnumber': forms.TextInput(attrs={'class': 'form-control'}),
        }

