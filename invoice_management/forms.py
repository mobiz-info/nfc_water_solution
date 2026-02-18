from datetime import date
from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms

from master.models import CategoryMaster

from . models import *

class InvoiceForm(forms.ModelForm):
    
    class Meta:
        model = Invoice
        fields = ['net_taxable','vat','amout_total','discount','amout_recieved','reference_no']
        
        widgets = {
            'reference_no': TextInput(attrs={'class': 'required form-control'}), 
            'net_taxable': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'vat': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'amout_total': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'discount': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'amout_recieved': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
        }
        
class InvoiceItemsForm(forms.ModelForm):
    
    class Meta:
        model = InvoiceItems
        fields = ['product_items','rate','total_including_vat','qty','remarks','category']

        widgets = {
            'category': Select(attrs={'class': 'required form-control product-category'}), 
            'product_items': Select(attrs={'class': 'required form-control product-item'}), 
            'rate': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Rate'}), 
            'qty': TextInput(attrs={'class': 'form-control product-qty','placeholder' : 'Enter QTY'}), 
            'total_including_vat': TextInput(attrs={'class': 'form-control total_including_vat','placeholder' : 'Enter Total'}), 
            'remarks': Textarea(attrs={'class': 'form-control','placeholder' : 'Serial Number Should be added here','rows':'2' }), 
        }
