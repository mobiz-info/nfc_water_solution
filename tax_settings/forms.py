from django import forms
from django.forms import ModelForm
from .models import *

class TaxTypesForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name','percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'percentage': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }