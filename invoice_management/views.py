from decimal import Decimal
import json
import random
import datetime
from datetime import date
# django
from django.db.models import Q, Sum, F
from django.urls import reverse
from django.utils import timezone
from django.forms import inlineformset_factory
from django.contrib.auth.models import User,Group
from django.forms.formsets import formset_factory
from django.db import transaction, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apiservices.views import delete_coupon_recharge
from client_management.models import ChequeCouponPayment, CustomerCoupon, CustomerCouponItems, CustomerCouponStock, CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyItems, OutstandingAmount
from client_management.views import handle_coupons, handle_invoice_deletion, handle_outstanding_amounts, update_van_product_stock
from coupon_management.models import CouponStock
from customer_care.models import DiffBottlesModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view,renderer_classes, permission_classes
#local
from accounts.models import Customers
from master.functions import generate_form_errors, generate_invoice_no
from master.models import CategoryMaster, RouteMaster
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from product.models import Product, Product_Default_Price_Level
from invoice_management.forms import InvoiceForm, InvoiceItemsForm
from invoice_management.serializers import BuildingNameSerializers, ProductSerializers,CustomersSerializers
from van_management.models import VanCouponStock,Van_Routes
from sales_management.models import Receipt
from sales_management.views import delete_receipt
from master.functions import log_activity
from django.db.models import Q, BooleanField, ExpressionWrapper
from django.db.models.functions import Now

# Create your views here.
@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_building_no(request,route_id):
    customers = Customers.objects.filter(is_guest=False, routes__pk=route_id)
    serialized = BuildingNameSerializers(customers, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_customer(request,route_id,building_no):
    customers = Customers.objects.filter(is_guest=False, routes__pk=route_id,building_name=building_no)
    serialized = CustomersSerializers(customers, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_products(request,category_id):
    category = Product.objects.filter(category_id__pk=category_id)
    serialized = ProductSerializers(category, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_customer_rate(request,product,customer):
    product_price = 0
    vat_rate = 0
    total_include_vat = 0
    # print(product)
    # print(customer)
    try :
        product = Product.objects.get(pk=product)
        customer = Customers.objects.get(pk=customer)
        product_price = Product_Default_Price_Level.objects.get(product_id=product,customer_type=customer.customer_type).rate
        
        if product.product_name.tax:
            # print('vat')
            vat_rate = product.product_name.tax.percentage
            # print(vat_rate)
            total_include_vat = (float(vat_rate)/100) * float(product_price)
            # print(total_include_vat, "vat")
        
        
        response_data = {
            "StatusCode" : 6000,
            'product_price':product_price,
            'total_include_vat':total_include_vat,
        }
    except:
        response_data = {
            "StatusCode" : 6001,
            'product_price':product_price,
            'total_include_vat':total_include_vat,
        }
    return Response(response_data, status=status.HTTP_200_OK)

@login_required
def invoice_info(request,pk):
    """
    single view of invoice
    :param request:
    :return: invoice single view
    """
    instance = Invoice.objects.get(pk=pk,is_deleted=False)
    
    log_activity(
        created_by=request.user,
        description=f"Viewed invoice with ID {pk}."
    )
    
    context = {
        'instance': instance,
        'page_name' : 'Invoice',
        'page_title' : 'Invoice',
        'is_invoice': True,
    }

    return render(request, 'invoice_management/info.html', context)

@login_required

def invoice_list(request):
    """
    FAST Invoice List (no can_edit)
    """

    filter_date = request.GET.get("date")
    route_name = request.GET.get("route_name")
    query = request.GET.get("q")

    filter_data = {}

    # -------------------- BASE QUERY --------------------
    instances = (
        Invoice.objects
        .filter(is_deleted=False)
        .select_related("customer")  # 🔥 avoid extra queries
        .order_by("-created_date")
    )

    # -------------------- DATE FILTER (INDEX FRIENDLY) --------------------
    if filter_date:
        filter_date = datetime.datetime.strptime(filter_date, "%Y-%m-%d").date()
        start = datetime.datetime.combine(filter_date, datetime.time.min)
        end = datetime.datetime.combine(filter_date, datetime.time.max)

        instances = instances.filter(created_date__range=(start, end))
        filter_data["filter_date"] = filter_date.strftime("%Y-%m-%d")

    # -------------------- SEARCH --------------------
    if query:
        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(customer__customer_name__icontains=query)
        )
        filter_data["q"] = query

    # -------------------- ROUTE FILTER --------------------
    if route_name:
        instances = instances.filter(customer__routes__route_name=route_name)
        filter_data["route_name"] = route_name

    # -------------------- ROUTES --------------------
    route_li = RouteMaster.objects.all()

    context = {
        "instances": instances,
        "page_name": "Invoice List",
        "page_title": "Invoice List",
        "filter_data": filter_data,
        "route_li": route_li,
        "is_invoice": True,
        "is_need_datetime_picker": True,
    }

    return render(request, "invoice_management/list.html", context)

@login_required
def invoice_customers(request):
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
        title = "Invoice Customers - %s" % query
        filter_data['q'] = query
        
    route_instances = RouteMaster.objects.all()

    log_activity(
        created_by=request.user,
        description="Viewed customer list for invoice creation." if not filter_data else f"Filtered customer list with filters: {filter_data}."
    )
    
    context = {
        'instances': instances,
        'route_instances' : route_instances,
        
        'page_title': 'Create invoice',
        'invoice_page': True,
        'is_need_datetime_picker': True
    }
    
    return render(request,'invoice_management/customer_list.html',context)

def create_invoice(request, customer_pk):
    # customer_pk = request.GET.get("customer_pk")
    customer_instance = Customers.objects.get(pk=customer_pk)
    InvoiceItemsFormset = formset_factory(InvoiceItemsForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        invoice_items_formset = InvoiceItemsFormset(request.POST,prefix='invoice_items_formset', form_kwargs={'empty_permitted': False})
        
        if invoice_form.is_valid() and invoice_items_formset.is_valid():
            
            # try:
            #     invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
            #     last_invoice_number = invoice_last_no.invoice_no
            #     prefix, date_part, number_part = last_invoice_number.split('-')
            #     new_number_part = int(number_part) + 1
            #     invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
            # except Invoice.DoesNotExist:
            #     date_part = timezone.now().strftime('%Y%m%d')
            #     random_part = str(random.randint(1000, 9999))
            #     invoice_number = f'WTR-{date_part}-{random_part}'
            
            try:
                with transaction.atomic():
                    invoice = invoice_form.save(commit=False)
                    invoice.created_date = datetime.datetime.today()
                    # invoice.invoice_no = generate_invoice_no(datetime.datetime.today().date())
                    invoice.customer = customer_instance
                    invoice.save()
                    
                    for form in invoice_items_formset:
                        data = form.save(commit=False)
                        data.invoice = invoice
                        data.save()
                    
                    log_activity(
                        created_by=request.user,
                        description=f"Invoice {invoice.invoice_no} created for customer {customer_instance.customer_name}."
                    ) 
                    
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Invoice created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('invoice:invoice_list')
                    }
                    
            except IntegrityError as e:
                log_activity(
                    created_by=request.user,
                    description=f"IntegrityError while creating invoice for customer {customer_instance.customer_name}: {str(e)}"
                )
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
            message = generate_form_errors(invoice_form,formset=False)
            message += generate_form_errors(invoice_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        invoice_form = InvoiceForm()
        invoice_items_formset = InvoiceItemsFormset(prefix='invoice_items_formset')
        
        context = {
            'invoice_form': invoice_form,
            'invoice_items_formset': invoice_items_formset,
            'customer_instance': customer_instance,
            
            'page_title': 'Create invoice',
            'invoice_page': True,
            'is_need_datetime_picker': True
        }
        
        return render(request,'invoice_management/create.html',context)


@login_required
def edit_invoice(request,pk):
    """
    edit operation of invoice
    :param request:
    :param pk:
    :return:
    """
    invoice_instance = get_object_or_404(Invoice, pk=pk)
    invoice_items = InvoiceItems.objects.filter(invoice=invoice_instance)
    customer_instance = invoice_instance.customer
    
    if invoice_items.exists():
        extra = 0
    else:
        extra = 1 

    InvoiceItemsFormset = inlineformset_factory(
        Invoice,
        InvoiceItems,
        extra=extra,
        form=InvoiceItemsForm,
    )
        
    message = ''
    
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST,instance=invoice_instance)
        invoice_items_formset = InvoiceItemsFormset(request.POST,request.FILES,
                                            instance=invoice_instance,
                                            prefix='invoice_items_formset',
                                            form_kwargs={'empty_permitted': False})            
        
        if invoice_form.is_valid() and  invoice_items_formset.is_valid() :
            #create
            data = invoice_form.save(commit=False)
            data.save()
            
            for form in invoice_items_formset:
                if form not in invoice_items_formset.deleted_forms:
                    i_data = form.save(commit=False)
                    if not i_data.invoice :
                        i_data.invoice = invoice_instance
                    i_data.save()

            for f in invoice_items_formset.deleted_forms:
                f.instance.delete()
            
            log_activity(
                        created_by=request.user,
                        description=f"Invoice {invoice_instance.invoice_no} updated for customer {customer_instance.customer_name}."
                    )
                
            response_data = {
                "status": "true",
                "title": "Successfully Updated",
                "message": "invoice Updated Successfully.",
                'redirect': 'true',
                "redirect_url": reverse('invoice:invoice_list'),
                "return" : True,
            }
    
        else:
            message = generate_form_errors(invoice_form,formset=False)
            message += generate_form_errors(invoice_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                        
    else:
        # initial_values = []
        # for invoice_item in invoice_items:
        #     category_id = invoice_item.product.category_id
        #     initial_values.append({'category': category_id})

        invoice_form = InvoiceForm(instance=invoice_instance,initial={'customer_id': invoice_instance.customer.pk})
        invoice_items_formset = InvoiceItemsFormset(queryset=invoice_items,
                                                    prefix='invoice_items_formset',
                                                    instance=invoice_instance)
        # category_ids = [invoice_item.product.category_id for invoice_item in invoice_items]

        # # Create a list of initial data for each form in the formset
        # initial_data = [{'category': category_id} for category_id in category_ids]

        # # Create the formset instance with initial data
        # invoice_items_formset = InvoiceItemsFormset(
        #     queryset=invoice_items,
        #     prefix='invoice_items_formset',
        #     instance=invoice_instance,
        #     initial=initial_data
        # )
                
        route_instances = RouteMaster.objects.all()
        building_names_queryset = Customers.objects.filter(is_guest=False, routes=invoice_form.instance.customer.routes).values_list('building_name', flat=True).distinct()
        # building_names = [name for name in building_names_queryset if isinstance(name, str) and name.strip()]
        

        context = {
            'invoice_form': invoice_form,
            'invoice_items_formset': invoice_items_formset,
            'route_instances': route_instances,
            'building_names': building_names_queryset,
            'customer_instance': customer_instance,
            
            'message': message,
            'page_name' : 'edit invoice',
            'url' : reverse('invoice:edit_invoice', args=[invoice_instance.pk]),
            'invoice_page': True,   
            'is_edit' : True,        
        }

        return render(request, 'invoice_management/create.html', context)
    
def delete_invoice(request, pk):
    """
    invoice deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    try:
        with transaction.atomic():
            invoice = Invoice.objects.get(pk=pk)
            log_activity(request.user, f"Attempting to delete invoice #{invoice.invoice_no}.")
            receipts = Receipt.objects.filter(invoice_number=invoice.invoice_no)
            for receipt in receipts:
                delete_receipt(request, receipt.receipt_number, receipt.customer.customer_id) 
                
            if CustomerSupply.objects.filter(invoice_no=invoice.invoice_no).exists():
                customer_supply_instance = get_object_or_404(CustomerSupply, invoice_no=invoice.invoice_no)
                supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=customer_supply_instance)
                five_gallon_qty = supply_items_instances.filter(product__product_name="5 Gallon").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
                
                DiffBottlesModel.objects.filter(
                    delivery_date__date=customer_supply_instance.created_date.date(),
                    assign_this_to=customer_supply_instance.salesman,
                    customer=customer_supply_instance.customer_id
                    ).update(status='pending')
                
                # Handle outstanding amount adjustments
                handle_outstanding_amounts(customer_supply_instance, five_gallon_qty)
                
                # Handle coupon deletions and adjustments
                handle_coupons(customer_supply_instance, five_gallon_qty)
                
                # Update van product stock and empty bottle counts
                update_van_product_stock(customer_supply_instance, supply_items_instances, five_gallon_qty)
                
                log_activity(request.user, f"Deleted customer supply for invoice #{invoice.invoice_no}.")
                # Mark customer supply and items as deleted
                customer_supply_instance.delete()
                supply_items_instances.delete()
                
            elif CustomerCoupon.objects.filter(invoice_no=invoice.invoice_no).exists():
                customer_coupons = CustomerCoupon.objects.filter(invoice_no=invoice.invoice_no)
                
                for customer_coupon in customer_coupons:
                    coupon_items = CustomerCouponItems.objects.filter(customer_coupon=customer_coupon)
                    for item in coupon_items:
                        coupon_stock = CustomerCouponStock.objects.get(customer=customer_coupon.customer,coupon_type_id=item.coupon.coupon_type)
                        # print(int(item.coupon.coupon_type.no_of_leaflets))
                        if coupon_stock.count >= int(item.coupon.coupon_type.no_of_leaflets):
                            coupon_stock.count -= int(item.coupon.coupon_type.no_of_leaflets)
                        else:
                            coupon_stock.count = 0
                        coupon_stock.save()
                        if invoice.created_date.date() == datetime.datetime.today().date():
                            van_coupon_stock = VanCouponStock.objects.get(coupon=item.coupon,created_date=invoice.created_date.date())
                        else:
                            van_coupon_stock = VanCouponStock.objects.create(
                                coupon=item.coupon,
                                created_date=datetime.datetime.today().date()
                                )
                        van_coupon_stock.stock += 1
                        van_coupon_stock.save()
                        
                        log_activity(request.user, f"Adjusted coupon stock for customer #{customer_coupon.customer.customer_id}.")
                        
                        item.delete()
                        
                        
                        coupon_stock_status = CouponStock.objects.get(couponbook=item.coupon)
                        coupon_stock_status.coupon_stock = "van"
                        coupon_stock_status.save()

                    InvoiceDailyCollection.objects.filter(invoice=invoice).delete()

                    ChequeCouponPayment.objects.filter(customer_coupon=customer_coupon).delete()
                    
                    balance_amount = invoice.amout_total - invoice.amout_recieved
                        
                    if invoice.amout_total > invoice.amout_recieved:
                        if CustomerOutstandingReport.objects.filter(customer=customer_coupon.customer, product_type="amount").exists():
                            customer_outstanding_report_instance = CustomerOutstandingReport.objects.get(customer=customer_coupon.customer, product_type="amount")
                            customer_outstanding_report_instance.value -= Decimal(balance_amount)
                            customer_outstanding_report_instance.save()
                            
                    elif invoice.amout_total < invoice.amout_recieved:
                        customer_outstanding_report_instance = CustomerOutstandingReport.objects.get(customer=customer_coupon.customer, product_type="amount")
                        customer_outstanding_report_instance.value += Decimal(balance_amount)
                        customer_outstanding_report_instance.save()
                    
                    customer_coupon.delete()
                
            if CustomerOutstanding.objects.filter(created_date__date=invoice.created_date.date(),customer=invoice.customer, invoice_no=invoice.invoice_no).exists():
                # Retrieve outstanding linked to the invoice
                outstanding = CustomerOutstanding.objects.filter(created_date__date=invoice.created_date.date(),customer=invoice.customer, invoice_no=invoice.invoice_no).delete()
                
                log_activity(request.user, f"Adjusted outstanding for invoice #{invoice.invoice_no}.")
                # Adjust CustomerOutstandingReport
                # report = CustomerOutstandingReport.objects.get(customer=outstanding.customer, product_type='amount')
                # report.value -= invoice.amout_total  # Adjust based on your invoice amount field
                # report.save()
                    
            invoice.is_deleted=True
            invoice.save()
            
            InvoiceItems.objects.filter(invoice=invoice).update(is_deleted=True)
            
            log_activity(request.user, f"Invoice #{invoice.invoice_no} successfully marked as deleted.")    

            response_data = {
                "status": "true",
                "title": "Successfully Deleted",
                "message": "Invoice and associated data successfully deleted and reversed.",
                "redirect": "true",
                "redirect_url": reverse('invoice:invoice_list'),
            }
            
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    except Invoice.DoesNotExist:
        log_activity(request.user, f"Invoice with ID {pk} not found.")
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "Invoice not found.",
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    except CustomerOutstanding.DoesNotExist:
        log_activity(request.user, f"Customer outstanding record not found for invoice #{pk}.")
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "Customer outstanding record not found.",
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    # except Exception as e:
    #     response_data = {
    #         "status": "false",
    #         "title": "Failed",
    #         "message": str(e),
    #     }
    #     return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type='application/javascript')

    # except Invoice.DoesNotExist:
    #     response_data = {
    #         "status": "false",
    #         "title": "Failed",
    #         "message": "Invoice not found.",
    #     }
    #     return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    # except CustomerOutstanding.DoesNotExist:
    #     response_data = {
    #         "status": "false",
    #         "title": "Failed",
    #         "message": "Customer outstanding record not found.",
    #     }
    #     return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    # except Exception as e:
    #     response_data = {
    #         "status": "false",
    #         "title": "Failed",
    #         "message": str(e),
    #     }
    #     return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type='application/javascript')

@login_required
def invoice(request,pk):
    """
    Invoice Download
    :param request:
    :return: Invoices Download view
    """
    
    instance = Invoice.objects.get(pk=pk,is_deleted=False)  
    log_activity(
        created_by=request.user,
        description=f"Viewed invoice with ID {pk}."
    )       
    context = {
        'instance': instance,
        'page_name' : 'Invoice',
        'page_title' : 'Invoice',
        
        'is_invoice': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'invoice_management/invoice.html', context)

@login_required

def customerwise_invoice(request):
    
    invoices = Invoice.objects.filter( invoice_status="non_paid",is_deleted=False).exclude(amout_total__lt=1)
    query = request.GET.get("q")
    route_filter = request.GET.get('route_name')

    if query:
            invoices = invoices.filter(
                Q(customer__customer_name__icontains=query) |
                Q(customer__routes__route_name__icontains=query)|
                Q(customer__custom_id__icontains=query)
            )

    if route_filter:
            invoices = invoices.filter(customer__routes__route_name=route_filter)

    route_li = RouteMaster.objects.all()
    invoices = invoices.values(
        'customer__customer_name',
        'customer__custom_id',
        'customer__routes__route_name',
        'customer__customer_id'
    ).distinct()

    log_activity(
        created_by=request.user,
        description="Viewed the customer-wise invoice list."
    )
    
    context = {
        'route_li':route_li,
        'invoices': invoices,
        
    }
    return render(request, 'invoice_management/customerwiseinvoice_list.html', context)
@login_required
def edit_customerwise_invoice(request,customer_id):
    print("customer_id",customer_id)
    invoices = Invoice.objects.filter(customer__customer_id=customer_id, invoice_status="non_paid",is_deleted=False).exclude(amout_total__lt=1)
    total_amount_total = 0
    total_amount_received = 0
    total_balance_amount = 0

    for invoice in invoices:
        invoice.balance_amount = invoice.amout_total - invoice.amout_recieved
        total_amount_total += invoice.amout_total
        total_amount_received += invoice.amout_recieved
        total_balance_amount += invoice.balance_amount

           
    log_activity(
        created_by=request.user,
        description=f"Edited invoices for customer with ID {customer_id}."
    )       
    context = {
        'invoices': invoices,
        'total_amount_total': total_amount_total,
        'total_amount_received': total_amount_received,
        'total_balance_amount': total_balance_amount,
    }
    return render(request, 'invoice_management/customerwiseinvoice.html', context)

from django.contrib import messages
def make_payment(request):
        if request.method == 'POST':
            customer_id = request.POST.get('customer_id')
            payment_amount = float(request.POST.get('payment_amount')) 
            
            customer = get_object_or_404(Customers, pk=customer_id)
            invoices = Invoice.objects.filter(
                customer=customer, 
                invoice_status="non_paid", 
                is_deleted=False
            ).exclude(amout_total__lt=1).order_by('created_date')

            with transaction.atomic():
                for invoice in invoices:
                    balance_amount = float(invoice.amout_total) - float(invoice.amout_recieved)  
                    if payment_amount > 0:
                        if payment_amount >= balance_amount:
                            invoice.amout_recieved = float(invoice.amout_recieved) + balance_amount 
                            invoice.invoice_status = "paid"
                            payment_amount -= balance_amount
                        else:
                            invoice.amout_recieved = float(invoice.amout_recieved) + payment_amount  
                            payment_amount = 0
                        invoice.save()
                    else:
                        break
            
            messages.success(request, 'Payment applied successfully!')
            return redirect('invoice:customerwise_invoice')

        return redirect('invoice:customerwise_invoice')


@login_required
def today_route_outstanding_list(request):
    today = date.today()

    route_name = request.GET.get('route_name')
    q = request.GET.get('q', '').strip()

    route_li = RouteMaster.objects.all()

    if not route_name and route_li.exists():
        route_name = route_li.first().route_name

    customers = Customers.objects.filter(
        routes__route_name=route_name,
        is_deleted=False
    )

    # 🔍 SEARCH FILTER (Customer Name OR Customer ID)
    if q:
        customers = customers.filter(
            Q(customer_name__icontains=q) |
            Q(custom_id__icontains=q)
        )

    customers = customers.distinct()

    result = []
    total_today_outstanding = Decimal("0.00")

    for customer in customers:
        invoice_totals = Invoice.objects.filter(
            customer=customer,
            created_date__date__lte=today,
            is_deleted=False,
            invoice_status="non_paid",
        ).aggregate(
            total_amount=Sum('amout_total'),
            total_received=Sum('amout_recieved')
        )

        total_amount = invoice_totals['total_amount'] or Decimal("0.00")
        total_received = invoice_totals['total_received'] or Decimal("0.00")

        today_outstanding = total_amount - total_received

        if today_outstanding > 0:
            customer.today_outstanding = today_outstanding
            total_today_outstanding += today_outstanding
            result.append(customer)

    context = {
        'instances': result,
        'route_li': route_li,
        'route_name': route_name,
        'q': q,
        'today': today,
        'total_today_outstanding': total_today_outstanding,
    }

    return render(
        request,
        'invoice_management/payment_adjust_route.html',
        context
    )



@login_required
def invoice_adjust(request, customer_id):
    today = date.today()
    customer = get_object_or_404(Customers, pk=customer_id)


    # 🔹 Status filter (GET only)
    status = request.GET.get("status", "non_paid")

    invoices = (
        Invoice.objects
        .filter(
            customer=customer,
            invoice_date__date__lte=today,
            is_deleted=False,
            invoice_status=status
        )
        .annotate(balance=F("amout_total") - F("amout_recieved"))
        .order_by("created_date")
    )

    if status == "non_paid":
        invoices = invoices.filter(balance__gt=0)

    if request.method == "POST":
        adjustment_date_str = request.POST.get("date")

        if not adjustment_date_str:
            messages.error(request, "Adjustment date is required")
            return redirect(request.path)

        adjustment_date = datetime.datetime.strptime(
            adjustment_date_str, "%Y-%m-%d"
        ).date()


    # 🔹 POST = adjustment
    if request.method == "POST":
        
        total_adjusted = Decimal("0.00")

        # IMPORTANT: process using POST keys, not queryset state
        invoice_ids = [
            key.replace("adjust_", "")
            for key in request.POST.keys()
            if key.startswith("adjust_")
        ]

        with transaction.atomic():
            for invoice_id in invoice_ids:
                invoice = Invoice.objects.select_for_update().get(
                    pk=invoice_id,
                    customer=customer,
                    is_deleted=False
                )
                print("salsemanId:",invoice.salesman.id)
                adjust_amount = Decimal(
                    request.POST.get(f"adjust_{invoice_id}", "0") or "0"
                )

                if adjust_amount <= 0:
                    continue

                balance = invoice.amout_total - invoice.amout_recieved

                if adjust_amount > balance:
                    messages.error(
                        request,
                        f"Adjustment exceeds balance for {invoice.invoice_no}"
                    )
                    return redirect(request.path)

                # 🔹 Update invoice
                invoice.amout_recieved += adjust_amount

                if invoice.amout_recieved >= invoice.amout_total:
                    invoice.amout_recieved = invoice.amout_total
                    invoice.invoice_status = "paid"
                else:
                    invoice.invoice_status = "non_paid"

                invoice.save(update_fields=["amout_recieved", "invoice_status"])

                
                customer_outstanding=CustomerOutstanding.objects.create(
                        customer=customer,
                        product_type="amount",
                        invoice_no = invoice.invoice_no,
                        created_date = today,
                        outstanding_date = adjustment_date,
                        created_by = invoice.salesman.id
                    )
                OutstandingAmount.objects.create(
                    customer_outstanding=customer_outstanding,
                    amount=-adjust_amount
                    
                )

                total_adjusted += adjust_amount

        messages.success(
            request,
            f"Payment adjusted successfully. Total adjusted: {total_adjusted}"
        )
        return redirect(f"{request.path}?status=non_paid")

    return render(
        request,
        "invoice_management/payment_adjust.html",
        {
            "customer": customer,
            "invoices": invoices,
            "status": status,
        }
    )