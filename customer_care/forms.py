from django import forms
from django.forms import ModelForm
from .models import *
from master.models import *
from client_management.models import *
from datetime import datetime, timedelta


class RequestType_Create_Form(forms.ModelForm):
    class Meta:
        model = RequestTypeMaster
        fields = ['request_name']
        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class RequestType_Edit_Form(forms.ModelForm):

    class Meta:
        model = RequestTypeMaster
        fields = ['request_name']
        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }


class CustomercreateForms(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_staff'].queryset = CustomUser.objects.filter(is_active = True,branch_id = branch,designation_id__designation_name = "Sales Executive")
        self.fields['routes'].queryset = RouteMaster.objects.filter(branch_id = branch)
        self.fields['location'].queryset = LocationMaster.objects.filter(branch_id = branch)

    class Meta:
        model = Customers
        fields = ['customer_name','building_name','door_house_no','floor_no','sales_staff','routes','location','mobile_no','whats_app','email_id','gps_latitude','gps_longitude','customer_type','sales_type','no_of_bottles_required','max_credit_limit','credit_days','no_of_permitted_invoices']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'door_house_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'floor_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'routes': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'location': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'whats_app': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email_id': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'gps_latitude': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'gps_longitude': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'sales_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'no_of_bottles_required': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','type':'number'}),
            'max_credit_limit': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','type':'number'}),
            'credit_days': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','type':'number'}),
            'no_of_permitted_invoices': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','type':'number'}),
        }


class CreateRequestTypeForm(forms.ModelForm):
    class Meta:
        model=RequestTypeMaster
        fields=[
            'request_type','request_name'
            ]
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'request_name': forms.Select(attrs={'class': 'form-control'})
        }
class ChangeofaddressForm(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['routes'].queryset = RouteMaster.objects.filter(branch_id = branch)
        self.fields['location'].queryset = LocationMaster.objects.filter(branch_id = branch)

    class Meta:
        model = Customers
        fields = ['customer_name','location','building_name','door_house_no','floor_no','routes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'location': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'door_house_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'floor_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'routes': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),


            # 'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
          
        }



class DefaultBottleQuantityForm(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
    class Meta:
        model = Customers
        fields = ['customer_name','no_of_bottles_required']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'no_of_bottles_required': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','type':'number'}),
            # 'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
          
        }

class CustodyPullOutForm(forms.ModelForm):
    def __init__(self,customer_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request_type'].queryset = RequestTypeMaster.objects.filter(request_name__in = ['Custody Pull Out'])
        customer_items = CustodyCustomItems.objects.filter(customer=customer_id).values_list('product', flat=True)
        self.fields['item_name'].queryset = Product.objects.filter(product_id__in=customer_items)
        #self.fields['qty_to_be_taken_out'].queryset = CustodyCustomItems.objects.filter(customer = customer_id).count

    class Meta:
        model = CustodyPullOutModel
        fields = ['request_type','item_name','qty_to_be_taken_out','scheduled_date','customer_custody_item']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'item_name': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'qty_to_be_taken_out': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'scheduled_date':forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': 'true'}),
            'customer_custody_item': forms.TextInput(attrs={'class': 'form-control','type':'hidden', 'required': 'true'}),
        }

class DiffBottles_Create_Form(forms.ModelForm):
    # def __init__(self,customer_id, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['request_type'].queryset = RequestTypeMaster.objects.filter(request_name__in = [])
    class Meta:
        model = DiffBottlesModel
        fields = ['product_item','quantity_required', 'delivery_date', 'assign_this_to', 'mode' ]

        widgets = {
            'product_item': forms.Select(attrs={'class': 'form-control', 'required': True}),  # Add widget for request_type
            'quantity_required': forms.TextInput(attrs={'class': 'form-control','required': False}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assign_this_to': forms.Select(attrs={'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-control'}),
        }


class Other_Req_Create_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request_type'].queryset = RequestTypeMaster.objects.exclude(request_name__in = ['Coupons','Dispenser','Empty Bottles','Filled Bottles'])

        
    class Meta:
        model = OtherRequirementModel
        fields = ['requirement','request_type']

        widgets = {
            'requirement': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'request_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),

           
        }

class Coupon_Create_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request_type'].queryset = RequestTypeMaster.objects.exclude(request_name__in = ['Custody Pull Out','Others'])
        self.fields['coupon_type'].choices = [
            (choice[0], choice[1]) for choice in self.fields['coupon_type'].choices]
        self.fields['category'].choices = [
            (choice[0], choice[1]) for choice in self.fields['category'].choices]
        self.fields['payment_status'].choices = [
            (choice[0], choice[1]) for choice in self.fields['payment_status'].choices]
    class Meta:
        model = CouponPurchaseModel
        fields = ['coupon_type','category','number_of_books','payment_status','amount','free_coupon','discount','delivery_date','request_type']

        widgets = {
            'coupon_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'number_of_books': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'payment_status': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'amount': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'free_coupon': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'discount': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': True}),
            'request_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),

        }

class DiffBottlesFilterForm(forms.Form):
    request_type = forms.CharField(max_length=100, required=False)
    # request_type = forms.ModelChoiceField(queryset=DiffBottlesModel.objects.values_list('request_type__request_name', flat=True).distinct(), empty_label='Select Product', required=False)


    def filter_data(self):
        request_type = self.cleaned_data.get('request_type')
        queryset = DiffBottlesModel.objects.all()
        if request_type:
            queryset = queryset.filter(request_type__request_name=request_type)
        return queryset

class ReassignRequestForm(forms.ModelForm):
    new_assignee = forms.CharField(max_length=100, required=True)
    new_delivery_date = forms.DateField(required=True)

    class Meta:
        model = DiffBottlesModel
        fields = ['assign_this_to', 'delivery_date']
        widgets = {
            'assign_this_to': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_assignee = cleaned_data.get('assign_this_to')
        # Check if the new assignee is a salesman
        if new_assignee:
            is_salesman = new_assignee.user_type == 'Salesman'  # Adjust as per your user model
            if not is_salesman:
                raise forms.ValidationError("The selected assignee must be a salesman.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.assign_this_to = self.cleaned_data['assign_this_to']
        instance.delivery_date = self.cleaned_data['delivery_date']
        # Assuming the new assignee is a salesman, add the salesman name
        instance.salesman_name = instance.assign_this_to.get_full_name()  # Adjust as per your user model
        if commit:
            instance.save()
        return instance
    
class CustomerRequestTypeForm(forms.ModelForm):
    class Meta:
        model = CustomerRequestType
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }
class CustomerRequestType_Edit_Form(forms.ModelForm):

    class Meta:
        model = CustomerRequestType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class CustomerForm(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_staff'].queryset = CustomUser.objects.filter(is_active = True,branch_id = branch,designation_id__designation_name = "Sales Executive")
        self.fields['routes'].queryset = RouteMaster.objects.filter(branch_id=branch)

    class Meta:
        model = Customers
        fields = [
            'customer_name', 'building_name', 'door_house_no', 'floor_no',
            'sales_staff', 'routes','emirate', 'location', 'mobile_no', 'whats_app',
            'email_id', 'gps_latitude', 'gps_longitude', 'customer_type','five_g_count_limit','eligible_foc','rate',
            'sales_type', 'no_of_bottles_required', 'max_credit_limit',
            'credit_days', 'no_of_permitted_invoices','is_active','is_calling_customer','gps_module_active'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'door_house_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'floor_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'false'}),
            'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'routes': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'emirate': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'location': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'whats_app': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email_id': forms.TextInput(attrs={'class': 'form-control', 'required': 'false'}),
            'gps_latitude': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'gps_longitude': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'five_g_count_limit': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'eligible_foc': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'rate': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'sales_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'no_of_bottles_required': forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}),
            'max_credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}),
            'credit_days': forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}),
            'no_of_permitted_invoices': forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}),
            'is_active': forms.CheckboxInput(attrs={}),
        }