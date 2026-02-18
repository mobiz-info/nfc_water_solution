from django import forms
from django.forms import ModelForm
from .models import *
from master.models import *
from customer_care.models import *



class User_Create_Form(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_user_types = ['Branch User', 'Customer']
        self.fields['user_type'].choices = [(value, label) for value, label in self.fields['user_type'].choices if value not in excluded_user_types]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error("password2", "Passwords do not match. Please enter the same password in both fields.")
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'username', 'user_type', 'password', 'branch_id', 'staff_id', 'designation_id', 'blood_group', 'permanent_address', "present_address", 'phone', 'email', 'labour_card_no', 'labour_card_expiry', 'driving_licence_no', 'driving_licence_expiry', 'licence_issued_by', 'visa_issued_by', 'visa_no', 'visa_expiry', 'emirates_id_no', 'emirates_expiry', 'health_card_no', 'health_card_expiry', 'base_salary', 'wps_percentage', 'wps_ref_no', 'insurance_no', 'insurance_expiry', 'insurance_company','nationality','visa_type','passport_number','passport_expiry','joining_date']
        widgets = {
            'first_name':forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'}),
            'visa_issued_by': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'licence_issued_by': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'branch_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'user_type': forms.Select(attrs={'class': 'form-control', 'required': 'true',}),
            'designation_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'staff_id': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','pattern': '[0-9]{10,15}', 'title': 'Enter a valid phone number'}),
            "blood_group" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "permanent_address" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "present_address" :forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "labour_card_no" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "labour_card_expiry" :  forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            "driving_licence_no" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "driving_licence_expiry" :   forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
            'visa_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'emirates_id_no':forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'health_card_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'base_salary': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'wps_percentage': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'wps_ref_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'insurance_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'insurance_company': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'visa_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'emirates_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'health_card_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date', 'required': False}),
            'insurance_expiry': forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            "nationality" :forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'visa_type': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'passport_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
        }


class User_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['visa_issued_by'].queryset = EmirateMaster.objects.filter()
        self.fields['designation_id'].queryset = DesignationMaster.objects.filter()
        self.fields['branch_id'].queryset = BranchMaster.objects.filter()
        self.fields['licence_issued_by'].queryset = EmirateMaster.objects.filter()
    class Meta:
        model = CustomUser
        fields = ['first_name','username' ,'branch_id', 'user_type', 'staff_id', 'designation_id','blood_group','permanent_address',"present_address", 'phone','email','labour_card_no','labour_card_expiry','driving_licence_no','driving_licence_expiry','licence_issued_by','visa_issued_by','visa_no','visa_expiry','emirates_id_no','emirates_expiry','health_card_no','health_card_expiry','base_salary','wps_percentage','wps_ref_no','insurance_no','insurance_expiry','insurance_company','nationality','visa_type','passport_number','passport_expiry','joining_date']
        widgets = {
            'first_name':forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'visa_issued_by': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'licence_issued_by': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'branch_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'user_type': forms.Select(attrs={'class': 'form-control', 'required': 'true',}),
          
            'designation_id': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'staff_id': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','pattern': '[0-9]{10,15}', 'title': 'Enter a valid phone number'}),
            "blood_group" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "permanent_address" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "present_address" :forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "labour_card_no" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "labour_card_expiry" :  forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            "driving_licence_no" : forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            "driving_licence_expiry" :   forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
            'visa_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'emirates_id_no':forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'health_card_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'base_salary': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'wps_percentage': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'wps_ref_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'insurance_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'insurance_company': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'visa_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'emirates_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'health_card_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date', 'required': False}),
            'insurance_expiry': forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': False}),
            "nationality" :forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'visa_type': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'passport_expiry': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': False}),
        }

class CustomercreateForm(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_staff'].queryset = CustomUser.objects.filter(is_active = True,branch_id = branch,designation_id__designation_name = "Sales Executive")
        self.fields['routes'].queryset = RouteMaster.objects.filter(branch_id = branch)
        # self.fields['location'].queryset = LocationMaster.objects.filter(branch_id = branch)
        # self.fields['location'].queryset = LocationMaster.objects.none()
    class Meta:
        
        model = Customers
        fields = ['customer_name','building_name','door_house_no','floor_no','sales_staff','routes','emirate','location','mobile_no','whats_app','email_id','gps_latitude','gps_longitude','customer_type','rate','sales_type','no_of_bottles_required','max_credit_limit','credit_days','no_of_permitted_invoices','is_calling_customer','five_g_count_limit', 'eligible_foc','gps_module_active']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'door_house_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'floor_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'routes': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'emirate':forms.Select(attrs={'class': 'form-control', 'required': True,'id':'id_emirate'}),
            'location': forms.Select(attrs={'class': 'form-control', 'required': True,'id':'id_location'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'whats_app': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email_id': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'gps_latitude': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'gps_longitude': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'rate': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'sales_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'no_of_bottles_required': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
            'max_credit_limit': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
            'credit_days': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
            'no_of_permitted_invoices': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
            'five_g_count_limit': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
            'eligible_foc': forms.TextInput(attrs={'class': 'form-control', 'required': True,'type':'number'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'customer_name', 'building_name', 'door_house_no', 'floor_no',
            'sales_staff', 'routes', 'sales_type'
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")
        return cleaned_data


class CustomerEditForm(forms.ModelForm):
    def __init__(self,branch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_staff'].queryset = CustomUser.objects.filter(is_active = True,branch_id = branch,designation_id__designation_name = "Sales Executive")
        self.fields['routes'].queryset = RouteMaster.objects.filter(branch_id=branch)
        # self.fields['emirate'].queryset = EmirateMaster.objects.filter()
        # self.fields['location'].queryset = LocationMaster.objects.filter(branch_id = branch)
        self.fields['rate'].widget.attrs['readonly'] = True
        
    class Meta:
        model = Customers
        fields = ['customer_name','building_name','door_house_no','floor_no','sales_staff','routes','emirate','location','mobile_no','whats_app','email_id','gps_latitude','gps_longitude','customer_type','rate','sales_type','no_of_bottles_required','max_credit_limit','credit_days','no_of_permitted_invoices','is_active','is_calling_customer','five_g_count_limit', 'eligible_foc','gps_module_active']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'door_house_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'floor_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'sales_staff': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'routes': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'emirate':forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'location': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'whats_app': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'email_id': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'gps_latitude': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'gps_longitude': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'rate': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'customer_type': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'sales_type': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'no_of_bottles_required': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'max_credit_limit': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'credit_days': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'no_of_permitted_invoices': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'is_active': forms.CheckboxInput(attrs={}),
            'five_g_count_limit': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
            'eligible_foc': forms.TextInput(attrs={'class': 'form-control', 'required': False,'type':'number'}),
        
        }
        
    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'customer_name', 'building_name', 'door_house_no', 'floor_no',
            'sales_staff', 'routes', 'sales_type'
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")
        return cleaned_data


class Day_OfVisit_Form(forms.ModelForm):
    class Meta:
        model = Staff_Day_of_Visit
        fields = ['monday','tuesday','wednesday', 'thursday', 'friday', 'saturday','sunday','week1','week2','week3','week4','week5']
        widgets = {
            'monday': forms.CheckboxInput(attrs={}),
            'tuesday': forms.CheckboxInput(attrs={}),
            'wednesday': forms.CheckboxInput(attrs={}),
            'thursday': forms.CheckboxInput(attrs={}),
            'friday': forms.CheckboxInput(attrs={}),
            'saturday': forms.CheckboxInput(attrs={}),
            'sunday': forms.CheckboxInput(attrs={}),
            'week1': forms.CheckboxInput(attrs={}),
            'week2': forms.CheckboxInput(attrs={}),
            'week3': forms.CheckboxInput(attrs={}),
            'week4': forms.CheckboxInput(attrs={}),
            'week5': forms.CheckboxInput(attrs={}),

        }
    def __init__(self, *args, **kwargs):
        super(Day_OfVisit_Form,self).__init__(*args, **kwargs)
        
        
class VisitScheduleForm(forms.Form):
    week1 = forms.CharField(required=False)
    week2 = forms.CharField(required=False)
    week3 = forms.CharField(required=False)
    week4 = forms.CharField(required=False)
    
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
CustomUser = get_user_model()

class CustomPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']
        
class CustomerPriceChangeForm(forms.ModelForm):

    class Meta:
        model = CustomerPriceChange
        fields = ['new_price']
        
        widgets = {
            'new_price': forms.TextInput(attrs={'class': 'form-control product_rates', 'required': 'true', 'value':'0.00'}),
        }

class ChangeUsernameForm(forms.ModelForm):
    username = forms.CharField(
        label="New Username",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['username']

class CustomerPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']
        