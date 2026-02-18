from datetime import date
from django.forms.widgets import TextInput,Textarea,Select
from django import forms

from . models import *

class CreditNoteForm(forms.ModelForm):
    
    class Meta:
        model = CreditNote
        fields = ['net_taxable','vat','amout_total','discount','amout_recieved','reason_for_return']
        
        widgets = {
            'net_taxable': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'vat': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'amout_total': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'discount': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'amout_recieved': TextInput(attrs={'class': 'required form-control text-right', 'style':'text-align: right;'}), 
            'reason_for_return': Textarea(attrs={'class': 'required form-control'}), 
        }
        
        
class CreditNoteItemsForm(forms.ModelForm):
    
    class Meta:
        model = CreditNoteItems
        fields = ['product','rate','total_including_vat','qty','remarks','category']

        widgets = {
            'category': Select(attrs={'class': 'required form-control product-category'}), 
            'product': Select(attrs={'class': 'required form-control product-item'}), 
            'rate': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Rate'}), 
            'qty': TextInput(attrs={'class': 'form-control product-qty','placeholder' : 'Enter QTY'}), 
            'total_including_vat': TextInput(attrs={'class': 'form-control total_including_vat','placeholder' : 'Enter Total'}), 
            'remarks': Textarea(attrs={'class': 'form-control','placeholder' : 'Serial Number Should be added here','rows':'2' }), 
        }
