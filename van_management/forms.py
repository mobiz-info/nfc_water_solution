from django import forms
from django.forms import ModelForm
from .models import *
from accounts.models import *
from master.models import *

class VanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = CustomUser.objects.filter(user_type='Driver')
        self.fields['salesman'].queryset = CustomUser.objects.filter(user_type__in=['Salesman','marketing_executive'])

    class Meta:
        model = Van
        fields = ['van_make', 'plate', 'renewal_date', 'insurance_expiry_date', 'capacity', 'branch_id','salesman','driver','bottle_count','van_type']

        widgets = {
            'van_make' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'plate' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'renewal_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': 'true'}),
            'insurance_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': 'true'}),
            'capacity' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'driver' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
            'salesman' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
            'bottle_count' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'van_type' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
        }


class EditVanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = CustomUser.objects.filter(user_type='Driver')
        self.fields['salesman'].queryset = CustomUser.objects.filter(user_type__in=['Sales Executive','Salesman'])

    class Meta:
        model = Van
        fields = ['van_make', 'plate', 'renewal_date', 'insurance_expiry_date', 'capacity', 'branch_id','salesman','driver','bottle_count','van_type']

        widgets = {
            'van_make' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'plate' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'renewal_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date','required': 'true'}),
            'insurance_expiry_date': forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': 'true'}),
            'capacity' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'driver' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
            'salesman' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
            'bottle_count' : forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'van_type' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
        }


class VanAssociationForm(forms.Form):
    van = forms.ModelChoiceField(queryset=Van.objects.all(), label='Select Van',        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
)
    driver = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user_type='Driver'), label='Select Driver' ,widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
)
    salesman = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user_type='Salesman'),        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
)

class EditAssignForm(forms.ModelForm):
    class Meta:
        model = Van
        fields = ['driver', 'salesman']

    def __init__(self, *args, **kwargs):
        super(EditAssignForm, self).__init__(*args, **kwargs)
        self.fields['driver'].queryset = CustomUser.objects.filter(user_type='driver')
        self.fields['salesman'].queryset = CustomUser.objects.filter(user_type='salesman')





class VanAssignRoutesForm(forms.ModelForm):
    class Meta:
        model = Van_Routes
        fields = [ 'routes']

        widgets = {
            'routes' : forms.Select(attrs={"class": "form-control", 'required': 'true'}),
        }

# Licence 
class Licence_Add_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = Van_License
        fields = ['van', 'emirate','license_no','expiry_date']
        widgets = {
            'van': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'emirate': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'license_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': 'true'}),
        }


class Licence_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['emirate'].queryset = EmirateMaster.objects.filter()
    class Meta:
        model = Van_License
        fields = ['emirate','expiry_date','license_no']
        widgets = {
            
            'emirate': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control','type':'date', 'required': 'true'}),
            'license_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),

        }




# Expense
class ExpenseHeadForm(forms.ModelForm):
    class Meta:
        model = ExpenseHead
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ExpenseAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].queryset = RouteMaster.objects.all()
        self.fields['van'].queryset = Van.objects.all()
    class Meta:
        model = Expense
        fields = ['expence_type', 'route', 'van', 'amount', 'expense_date', 'remarks']
        widgets = {
            'expence_type': forms.Select(attrs={'class': 'form-control'}),
            'route': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'van': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
class ExpenseEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].queryset = RouteMaster.objects.all()
        self.fields['van'].queryset = Van.objects.all()
    class Meta:
        model = Expense
        fields = ['route', 'van', 'amount', 'expense_date', 'remarks']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'van': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
        
class BottleAllocationForm(forms.ModelForm):
    class Meta:
        model = BottleAllocation
        fields = ['route', 'fivegallon_count', 'reason']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-control'}),
            'fivegallon_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 

class ExcessBottleCountForm(forms.ModelForm):
    class Meta:
        model = ExcessBottleCount
        fields = ['van', 'bottle_count', 'route']
        

class VanProductStockForm(forms.ModelForm):
    class Meta:
        model = VanProductStock
        fields = ["opening_count","change_count","damage_count","empty_can_count","return_count","requested_count","pending_count","sold_count","stock","foc"]
        
        widgets = {
            'opening_count': forms.TextInput(attrs={'class':'form-control'}),
            # 'closing_count': forms.TextInput(attrs={'class':'form-control'}),
            'change_count': forms.TextInput(attrs={'class':'form-control'}),
            'damage_count': forms.TextInput(attrs={'class':'form-control'}),
            'empty_can_count': forms.TextInput(attrs={'class':'form-control'}),
            'return_count': forms.TextInput(attrs={'class':'form-control'}),
            'requested_count': forms.TextInput(attrs={'class':'form-control'}),
            'pending_count': forms.TextInput(attrs={'class':'form-control'}),
            'sold_count': forms.TextInput(attrs={'class':'form-control'}),
            'stock': forms.TextInput(attrs={'class':'form-control'}),
            'foc': forms.TextInput(attrs={'class':'form-control'}),
        }
        
        
class SalesmanCustomerRequestTypeForm(forms.ModelForm):
    class Meta:
        model = SalesmanCustomerRequestType
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }
class SalesmanCustomerRequestType_Edit_Form(forms.ModelForm):

    class Meta:
        model = SalesmanCustomerRequestType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }


class FreelanceVehicleRateChangeForm(forms.ModelForm):
    class Meta:
        model = FreelanceVehicleRateChange
        fields = [ 'new_rate']
        widgets = {
            'new_rate': forms.TextInput(attrs={'class': 'form-control product_rates', 'required': 'true', 'value':'0.00'}),
        }
        
class FreelanceVanProductIssueForm(forms.ModelForm):
    class Meta:
        model = FreelanceVanProductIssue
        fields = [ 'product', 'empty_bottles', 'extra_bottles',  'status']
        widgets = {
            # 'van': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'empty_bottles': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'extra_bottles': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['van'].queryset = Van.objects.filter(van_type="Freelance")


class VanSaleDamageForm(forms.ModelForm):
    class Meta:
        model = VanSaleDamage
        fields = ['product', 'reason', 'damage_from', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'damage_from': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }