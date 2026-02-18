import json
import random
import datetime
# django
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.forms import inlineformset_factory
from django.contrib.auth.models import User,Group
from django.forms.formsets import formset_factory
from django.db import transaction, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
#local
from master.functions import generate_form_errors
from master.models import RouteMaster
from accounts.models import Customers
from credit_note.forms import CreditNoteForm, CreditNoteItemsForm
from credit_note.models import CreditNote, CreditNoteItems

@login_required
def credit_note_info(request,pk):
    """
    single view of credit_note
    :param request:
    :return: credit_note single view
    """
    instance = CreditNote.objects.get(pk=pk,is_deleted=False)
    
    context = {
        'instance': instance,
        'page_name' : 'CreditNote',
        'page_title' : 'CreditNote',
        'is_credit_note': True,
    }

    return render(request, 'credit_note_management/credit_note.html', context)

@login_required
def credit_note_list(request):
    """
    CreditNote List
    :param request:
    :return: CreditNotes list view
    """
    
    instances = CreditNote.objects.filter(is_deleted=False).order_by("-created_date")
         
    date_range = ""
    date_range = request.GET.get('date_range')
    # print(date_range)

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(credit_note_no__icontains=query) |
            Q(product__credit_note_id__icontains=query) 
        )
        title = "CreditNote List - %s" % query
        filter_data['q'] = query
    
    context = {
        'instances': instances,
        'page_name' : 'CreditNote List',
        'page_title' : 'CreditNote List',
        'filter_data' :filter_data,
        'date_range': date_range,
        
        'is_credit_note': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'credit_note_management/list.html', context)

@login_required
def credit_note_customers(request):
    filter_data = {}
    
    instances = Customers.objects.all()
    
    if request.GET.get('route'):
        instances = instances.filter(routes__pk=request.GET.get('route'))
        
    if request.GET.get('building_no'):
        instances = instances.filter(door_house_no=request.GET.get('building_no'))
    
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(customer_id__icontains=query) |
            Q(mobile_no__icontains=query) |
            Q(whats_app__icontains=query) |
            Q(customer_name__icontains=query) 
        )
        title = "CreditNote Customers - %s" % query
        filter_data['q'] = query
        
    route_instances = RouteMaster.objects.all()

    context = {
        'instances': instances,
        'route_instances' : route_instances,
        
        'page_title': 'Create credit note',
        'credit_note_page': True,
        'is_need_datetime_picker': True
    }
    
    return render(request,'credit_note_management/customer_list.html',context)

@login_required
def create_credit_note(request, customer_pk):
    # customer_pk = request.GET.get("customer_pk")
    customer_instance = Customers.objects.get(pk=customer_pk)
    CreditNoteItemsFormset = formset_factory(CreditNoteItemsForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        credit_note_form = CreditNoteForm(request.POST)
        credit_note_items_formset = CreditNoteItemsFormset(request.POST,prefix='credit_note_items_formset', form_kwargs={'empty_permitted': False})
        
        if credit_note_form.is_valid() and credit_note_items_formset.is_valid():
            
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = str(random.randint(1000, 9999))
            credit_note_number = f'WTR-{date_part}-{random_part}'
            
            try:
                with transaction.atomic():
                    credit_note = credit_note_form.save(commit=False)
                    credit_note.created_date = datetime.today()
                    credit_note.credit_note_no = credit_note_number
                    credit_note.customer = customer_instance
                    credit_note.save()
                    
                    for form in credit_note_items_formset:
                        data = form.save(commit=False)
                        data.credit_note = credit_note
                        data.save()
                    
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "CreditNote created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('credit_note:credit_note_list')
                    }
                            
            except IntegrityError as e:
                # Handle database integrity error
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }

            except Exception as e:
                # Handle other exceptions
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }
        else:
            message = generate_form_errors(credit_note_form,formset=False)
            message += generate_form_errors(credit_note_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        credit_note_form = CreditNoteForm()
        credit_note_items_formset = CreditNoteItemsFormset(prefix='credit_note_items_formset')
        
        context = {
            'credit_note_form': credit_note_form,
            'credit_note_items_formset': credit_note_items_formset,
            'customer_instance': customer_instance,
            
            'page_title': 'Create credit_note',
            'credit_note_page': True,
            'is_need_datetime_picker': True
        }
        
        return render(request,'credit_note_management/create.html',context)

@login_required
def edit_credit_note(request,pk):
    """
    edit operation of credit_note
    :param request:
    :param pk:
    :return:
    """
    credit_note_instance = get_object_or_404(CreditNote, pk=pk)
    credit_note_items = CreditNoteItems.objects.filter(credit_note=credit_note_instance)
    customer_instance = credit_note_instance.customer
    
    if credit_note_items.exists():
        extra = 0
    else:
        extra = 1 

    CreditNoteItemsFormset = inlineformset_factory(
        CreditNote,
        CreditNoteItems,
        extra=extra,
        form=CreditNoteItemsForm,
    )
        
    message = ''
    
    if request.method == 'POST':
        credit_note_form = CreditNoteForm(request.POST,instance=credit_note_instance)
        credit_note_items_formset = CreditNoteItemsFormset(request.POST,request.FILES,
                                            instance=credit_note_instance,
                                            prefix='credit_note_items_formset',
                                            form_kwargs={'empty_permitted': False})            
        
        if credit_note_form.is_valid() and  credit_note_items_formset.is_valid() :
            #create
            data = credit_note_form.save(commit=False)
            data.save()
            
            for form in credit_note_items_formset:
                if form not in credit_note_items_formset.deleted_forms:
                    i_data = form.save(commit=False)
                    if not i_data.credit_note :
                        i_data.credit_note = credit_note_instance
                    i_data.save()

            for f in credit_note_items_formset.deleted_forms:
                f.instance.delete()
                
            response_data = {
                "status": "true",
                "title": "Successfully Updated",
                "message": "credit_note Updated Successfully.",
                'redirect': 'true',
                "redirect_url": reverse('credit_note:credit_note_list'),
                "return" : True,
            }
    
        else:
            message = generate_form_errors(credit_note_form,formset=False)
            message += generate_form_errors(credit_note_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                        
    else:
        credit_note_form = CreditNoteForm(instance=credit_note_instance,initial={'customer_id': credit_note_instance.customer.pk})
        credit_note_items_formset = CreditNoteItemsFormset(queryset=credit_note_items,
                                                    prefix='credit_note_items_formset',
                                                    instance=credit_note_instance)
                
        route_instances = RouteMaster.objects.all()
        building_names_queryset = Customers.objects.filter(is_guest=False, routes=credit_note_form.instance.customer.routes).values_list('building_name', flat=True).distinct()

        context = {
            'credit_note_form': credit_note_form,
            'credit_note_items_formset': credit_note_items_formset,
            'route_instances': route_instances,
            'building_names': building_names_queryset,
            'customer_instance': customer_instance,
            
            'message': message,
            'page_name' : 'edit credit_note',
            'url' : reverse('credit_note:edit_credit_note', args=[credit_note_instance.pk]),
            'credit_note_page': True,   
            'is_edit' : True,        
        }

        return render(request, 'credit_note_management/create.html', context)
    
@login_required
def delete_credit_note(request, pk):
    """
    credit_note deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    credit_note = CreditNote.objects.get(pk=pk)
    credit_note.is_deleted=True
    credit_note.save()
        
    CreditNoteItems.objects.filter(credit_note=credit_note).update(is_deleted=True)
    
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "credit_note Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('credit_note:credit_note_list'),
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def credit_note(request,pk):
    """
    CreditNote Download
    :param request:
    :return: CreditNotes Download view
    """
    
    instance = CreditNote.objects.get(pk=pk,is_deleted=False)  
           
    context = {
        'instance': instance,
        'page_name' : 'CreditNote',
        'page_title' : 'CreditNote',
        
        'is_credit_note': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'credit_note_management/credit_note.html', context)