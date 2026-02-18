import json
from datetime import datetime

from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404

from . models import *
from . forms import  *
from tax_settings.models import Tax
from tax_settings.forms import TaxTypesForm


# Create your views here.
def tax_types(request):
    instances = Tax.objects.all()
    context = {
        'instances': instances,
        'is_tax_pages' : True,
        }
    return render(request, 'tax/list.html', context)

def create_tax_type(request):
    
    if request.method == 'POST':
        form = TaxTypesForm(request.POST)
        
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Tax created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('tax_settings:tax_types')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            messages.error(request, 'Invalid form data. Please check the input.')
    else:
        form = TaxTypesForm()
    
    context = {
        'form': form,
        'is_tax_pages' : True,
        }
    
    return render(request, 'tax/create.html', context)

def edit_tax_type(request, pk):
    
    instance = get_object_or_404(Tax, pk=pk)
    
    if request.method == 'POST':
        form = TaxTypesForm(request.POST, instance=instance)
    
        if form.is_valid():
    
            data = form.save(commit=False)
            # print(data,"data")
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Tax Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('tax_settings:tax_types')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = TaxTypesForm(instance=instance)
        
    context = {
        'form': form,
        'is_tax_pages' : True,
    }
    return render(request, 'tax/create.html', context)

def delete_tax_type(request, pk):
    """
    delete tax,
    :param request:
    :param pk:
    :return:
    """
    instance = Tax.objects.get(pk=pk)
    instance.delete()
    
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Tax Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('tax_settings:tax_types'),
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')