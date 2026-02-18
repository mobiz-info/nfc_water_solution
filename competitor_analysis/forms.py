from django import forms
from .models import Competitor
from .models import CompetitorAnalysis

class CompetitorForm(forms.ModelForm):
    class Meta:
        model = Competitor
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
          
        }



class CompetitorAnalysisForm(forms.ModelForm):
    class Meta:
        model = CompetitorAnalysis
        fields = ['competitor', 'price', 'quantity', 'customer']
        widgets = {
            'competitor': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': '00.00'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'customer': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
           
        }

from master.models import RouteMaster

class CompetitorAnalysisFilterForm(forms.Form):
    route_name = forms.ModelChoiceField(
        queryset=RouteMaster.objects.all(),
        empty_label="All Routes",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
    )