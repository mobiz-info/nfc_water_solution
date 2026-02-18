from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from . forms import  *
from accounts.models import *
from master.models import *
from product.models import *

import json
from django.core.serializers import serialize
from django.views import View
from datetime import datetime
from client_management.models import CustodyCustomItems
from master.forms import *
# Create your views here.
from accounts.models import Customers
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
import calendar
from datetime import date, timedelta
from django.db.models import Max
from apiservices.notification import *
from master.functions import log_activity


class RequestType_List(View):
    template_name = 'customer_care/requesttype_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        category_li = RequestTypeMaster.objects.all()
        context = {'category_li': category_li}
        return render(request, self.template_name, context)

class RequestType_Create(View):
    template_name = 'customer_care/customer_requesttype_create.html'
    form_class = CustomerRequestTypeForm

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            messages.success(request, 'Category Successfully Added.', 'alert-success')
            return redirect('requesttype_list')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class RequestType_Edit(View):
    template_name = 'customer_care/requesttype_edit.html'
    form_class = RequestType_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = RequestTypeMaster.objects.get(request_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = RequestTypeMaster.objects.get(request_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Category Data Successfully Updated', 'alert-success')
            return redirect('requesttype_list')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class RequestType_Details(View):
    template_name = 'customer_care/requesttype_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        category_det = RequestTypeMaster.objects.get(request_id=pk)
        context = {'category_det': category_det}
        return render(request, self.template_name, context)
    
class RequestType_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(RequestTypeMaster, request_id=pk)
        rec.delete()
        messages.success(request, 'Request type deleted successfully', 'alert-success')
        return redirect('requesttype_list')

    def post(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(RequestTypeMaster, request_id=pk)
        rec.delete()
        messages.success(request, 'Request type deleted successfully', 'alert-success')
        return redirect('requesttype_list')





def createcustomer(request):
    branch = request.user.branch_id
    form = CustomercreateForms(branch)
    template_name = 'accounts/create_customer.html'
    context = {"form":form}
    try:
        if request.method == 'POST':
            form = CustomercreateForms(branch,data = request.POST)
            context = {"form":form}
            if form.is_valid():
                data = form.save(commit=False)
                data.created_by = str(request.user)
                data.created_date = datetime.now()
                data.emirate = data.location.emirate
                branch_id=request.user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)  # Adjust the criteria based on your model
                data.branch_id = branch
                data.save()
                Staff_Day_of_Visit.objects.create(customer = data)
                messages.success(request, 'Customer Created successfully!')
                return redirect('requestType')
            else:
                messages.success(request, 'Invalid form data. Please check the input.')
                return render(request, template_name,context)
        return render(request, template_name,context)
    except Exception as e:
            print(":::::::::::::::::::::::",e)
            messages.success(request, 'Something went wrong')
            return render(request, template_name,context)

def requestType(request):
    all_requestType = Customers.objects.all()
    print("hdfhjfasH",all_requestType)
    context = {'all_requestType': all_requestType}
    return render(request, 'customer_care/all_customers.html', context)

class requestType(View):
    template_name = 'customer_care/all_customers.html'

    def get(self, request, *args, **kwargs):
        # Retrieve the query parameter
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        # Start with all customers
        user_li = Customers.objects.all()

        # Apply filters if they exist
        if query:
            user_li = user_li.filter(
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(routes__route_name__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)

        # Get all route names for the dropdown
        route_li = RouteMaster.objects.all()

        context = {'user_li': user_li, 'route_li': route_li}
        return render(request, self.template_name, context)
    

class new_customer_request(View):
    template_name = 'customer_care/new_request.html'

    def get(self, request, *args, **kwargs):
        # Retrieve the query parameter
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        # Start with all customers
        user_li = CustomerOrders.objects.all()

        # Apply filters if they exist
        if query:
            user_li = user_li.filter(
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(routes__route_name__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)

        # Get all route names for the dropdown
        route_li = RouteMaster.objects.all()

        context = {'user_li': user_li, 'route_li': route_li}
        return render(request, self.template_name, context)
    

         

def change_of_address(request,pk):
    branch = request.user.branch_id
    cust_Data = Customers.objects.get(customer_id = pk)
    form = ChangeofaddressForm(branch,instance = cust_Data)
    template_name = 'customer_care/changeofaddress.html'
    context = {"form":form}
    try:
        if request.method == 'POST':
            form = ChangeofaddressForm(branch,instance = cust_Data,data = request.POST)
            context = {"form":form}
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, 'Customer Details Updated successfully!')
                return redirect('requestType')
            else:
                messages.success(request, 'Invalid form data. Please check the input.')
                return render(request, template_name,context)
        return render(request, template_name,context)
    except Exception as e:
        print(":::::::::::::::::::::::",e)
        messages.success(request, 'Something went wrong')
        return render(request, template_name,context)                      
   

def default_bottle_qty(request,pk):
    branch = request.user.branch_id
    cust_Data = Customers.objects.get(customer_id = pk)
    form = DefaultBottleQuantityForm(branch,instance = cust_Data)
    template_name = 'customer_care/default_bottleqty.html'
    context = {"form":form}
    try:
        if request.method == 'POST':
            form = DefaultBottleQuantityForm(branch,instance = cust_Data,data = request.POST)
            context = {"form":form}
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, 'Default bottle qty Updated successfully!')
                return redirect('requestType')
            else:
                messages.success(request, 'Invalid form data. Please check the input.')
                return render(request, template_name,context)
        return render(request, template_name,context)
    except Exception as e:
        print(":::::::::::::::::::::::",e)
        messages.success(request, 'Something went wrong')
        return render(request, template_name,context)                   
   
def get_item_quantity(request):
    if request.method == "GET":
        try:
            customer = request.GET['customer']
            item_name = request.GET['item_name']
            item_count = CustodyCustomItems.objects.get(customer=customer,product=item_name)
            dat = {'item_count': item_count.count,'customer_custody_item':item_count.custody_item_id}
            return JsonResponse(dat)
        except:
            dat = {'item_count': ''}
            return JsonResponse(dat)
   
def custody_pullout(request, pk):
    cust_data = Customers.objects.get(customer_id=pk)
    count = CustodyCustomItems.objects.get(customer=cust_data).count
    item_name = CustodyCustomItems.objects.get(customer=cust_data).product

    template_name = 'customer_care/custodypullout.html'
    context = {"count": count, "item_name": item_name, "cust_data": cust_data}

    try:
        if request.method == 'POST':
            item_name = request.POST.get('name')
            print("item_name", item_name)
            scheduled_date = request.POST.get('Scheduleddate')
            count = request.POST.get('count')
            print("count", count)

            form = CustodyPullOutForm(request.POST)

            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, 'Default bottle qty Updated successfully!')
                return redirect('requestType')
            else:
                messages.error(request, 'Invalid form data. Please check the input.')
                context["form"] = form
                return render(request, template_name, context)

        # GET request
        form = CustodyPullOutForm(
            initial={'item_name': item_name, 'qty_to_be_taken_out': count, 'scheduled_date': scheduled_date}
        )
        context["form"] = form

        return render(request, template_name, context)

    except Exception as e:
        print(":::::::::::::::::::::::", e)
        messages.error(request, 'Something went wrong')
        return render(request, template_name, context)
    
class Bottle_List(ListAPIView):
    template_name = 'customer_care/bottle_list.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        id_customer = Customers.objects.get(customer_id=pk).customer_id
        bottle_list_exists = DiffBottlesModel.objects.filter(customer=pk).exists()
        bottle_list=[]
        if bottle_list_exists:
            bottle_list = DiffBottlesModel.objects.filter(customer=pk)
        context = {'bottle_list': bottle_list,'customer_id':id_customer}
        return render(request,'customer_care/bottle_list.html',context)

    

class Diffbottles_Create(View):
    template_name = 'customer_care/bottle_create.html'
    form_class = DiffBottles_Create_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        try:
            id_customer = Customers.objects.get(customer_id=pk).customer_id
            context = {'form': self.form_class}
            return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request, self.template_name, context)
        

    def post(self, request, pk, *args, **kwargs):
        try:
            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                id_customer = Customers.objects.get(customer_id=pk)
                data.customer = id_customer
                data.created_by = str(request.user.id)
                data.save()
                messages.success(request, 'Bottles Successfully Added.', 'alert-success')
                return redirect('requestType')
            else:
            #print(form.errors)
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Field: {field}, Error: {error}")
                messages.success(request, 'Data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request,'customer_care/bottle_create.html')
        


class Other_List(ListAPIView):
    template_name = 'customer_care/other_list.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        id_customer = Customers.objects.get(customer_id=pk).customer_id
        other_list_exists = OtherRequirementModel.objects.filter(customer=pk).exists()
        other_list=[]
        if other_list_exists:
            other_list = OtherRequirementModel.objects.filter(customer=pk)
            print('other_list',other_list)
        context = {'other_list': other_list,'customer_id':id_customer}
        return render(request,'customer_care/other_list.html',context)
        
class Other_Req_Create(View):
    template_name = 'customer_care/otherrequirement_create.html'
    form_class = Other_Req_Create_Form
    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):        
        try:
            id_customer = Customers.objects.get(customer_id=pk).customer_id
            #requestype_obj = RequestTypeMaster.objects.exclude(request_name__in = ['Coupons','Others'])
            #print("requestype_obj=====",requestype_obj)
            context = {'form': self.form_class}            
            return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request, self.template_name, context)
        
    def post(self, request, pk, *args, **kwargs):
        try:
            print(request.POST,"====")
            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                id_customer = Customers.objects.get(customer_id=pk)
                data.customer = id_customer
                data.created_by = str(request.user.id)
                data.save()
                messages.success(request, 'requirement Successfully Added.', 'alert-success')
                return redirect('requestType')
            else:
            #print(form.errors)
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Field: {field}, Error: {error}")
                messages.success(request, 'Data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request,'customer_care/otherrequirement_create.html')
        
class Custody_Pullout_List(ListAPIView):
    template_name = 'customer_care/custody_pullout_list.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        id_customer = Customers.objects.get(customer_id=pk).customer_id
        custody_pullout_list=[]
        custody_customer_exists = CustodyCustomItems.objects.filter(customer=id_customer).exists()
        if custody_customer_exists:
            # count = CustodyCustomItems.objects.get(customer=id_customer).count
            # print('count',count)
            # item_name = CustodyCustomItems.objects.get(customer=id_customer).product
            # print("item_name",item_name)
            custody_pullout_list_exists = CustodyPullOutModel.objects.filter(customer=pk).exists()
            if custody_pullout_list_exists:
                custody_pullout_list = CustodyPullOutModel.objects.filter(customer=pk)
                print('custody_pullout_list',custody_pullout_list)
        context = {'custody_pullout_list': custody_pullout_list,'customer_id':id_customer}
        return render(request,'customer_care/custody_pullout_list.html',context)



        
class Custody_Pullout_Create(View):
    template_name = 'customer_care/custody_pullout_create.html'
    form_class = CustodyPullOutForm

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):        
        try:
            id_customer = Customers.objects.get(customer_id=pk).customer_id
            #requestype_obj = RequestTypeMaster.objects.exclude(request_name__in = ['Coupons','Others'])
            #print("requestype_obj=====",requestype_obj)
            form_instance = self.form_class(id_customer)

            context = {'form': form_instance,'customer':id_customer} 
            print(context,"contex")           
            return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request, self.template_name, context)
        
    def post(self, request, pk, *args, **kwargs):
        try:
            form = self.form_class(pk,request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                id_customer = Customers.objects.get(customer_id=pk)
                data.customer = id_customer
                data.created_by = str(request.user.id)
                data.save()
                messages.success(request, 'Custody Pullout Successfully Added.', 'alert-success')
                return redirect('custody_pullout_list',pk)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Field: {field}, Error: {error}")
                messages.success(request, 'Data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Exception as e:
            print("error",e)
            return render(request,'customer_care/custody_pullout_create.html')
        
class Coupon_Purchse_List(ListAPIView):
    template_name = 'customer_care/coupon_list.html' 

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        id_customer = Customers.objects.get(customer_id=pk).customer_id
        coupon_list_exists = CouponPurchaseModel.objects.filter(customer=pk).exists()
        coupon_list=[]
        if coupon_list_exists:
            coupon_list = CouponPurchaseModel.objects.filter(customer=pk)
            print('coupon_list',coupon_list)
        context = {'coupon_list': coupon_list,'customer_id':id_customer}
        return render(request,'customer_care/coupon_list.html',context)

class Coupon_Purchse_Create(View):
    template_name = 'customer_care/coupon_create.html'
    form_class = Coupon_Create_Form


    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        try:
            id_customer = Customers.objects.get(customer_id=pk).customer_id
            context = {'form': self.form_class}
            return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request, self.template_name, context)
        

    def post(self, request, pk, *args, **kwargs):
        try:
            print(request.POST,"====")
            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                id_customer = Customers.objects.get(customer_id=pk)
                data.customer = id_customer
                data.created_by = str(request.user.id)
                data.save()
                
                # Calculate the number of leaflets purchased
                no_of_leaflets = data.number_of_books  # Assuming `no_of_leaflets` is a field in your form/model
                
                # Update total leaflets count for the customer
                total_leaflets = CouponLeaflet.objects.filter(customer=id_customer).count()  # Assuming this is the correct way to get the total leaflets

                # Send notification
                try:
                    notification_body = (
                        f'Thank you for purchasing the coupon book. '
                        f'Number of leaflets: {no_of_leaflets}. '
                        f'Your total leaflets count is {total_leaflets}.'
                    )
                    notification(id_customer.user_id.pk, "Coupon Purchase", notification_body, "Sanawatercustomer")
                except Exception as e:
                    print(f"Notification error: {e}")
                    messages.error(request, f'Error sending notification: {e}', 'alert-danger')

                messages.success(request, 'Coupon purchased Successfully .', 'alert-success')
                return redirect('requestType')
            else:
            #print(form.errors)
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Field: {field}, Error: {error}")
                messages.success(request, 'Data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request,'customer_care/coupon_create.html')
        


# def get_weeks_in_month(year, month):
#     _, last_day = calendar.monthrange(year, month)
#     cal = calendar.Calendar()
#     days_in_month = cal.itermonthdays(year, month)
#     weeks = []
#     current_week = []
#     current_week_number = 1
#     for day in days_in_month:
#         if day != 0:
#             current_week.append(day)
#             if len(current_week) == 7 or day == last_day:
#                 weeks.append((current_week_number, current_week))
#                 current_week_number += 1
#                 current_week = []
#     return weeks

# def find_next_schedule_date(current_year, current_month):
#     # Get the weeks in the current month
#     weeks_in_month = get_weeks_in_month(current_year, current_month)
    
#     # Get the current date
#     today = date.today()
    
#     # Initialize variables to store the next schedule date
#     next_schedule_date = ''
    
#     # Iterate over the weeks to find the next schedule date
#     for week_number, week_days in weeks_in_month:
#         for day in week_days:
#             # Check if the day is greater than or equal to today's date
#             if date(current_year, current_month, day) >= today:
#                 next_schedule_date = date(current_year, current_month, day)
#                 break
#         if next_schedule_date:
#             break
    
#     return next_schedule_date
        

# def find_next_delivery_date(customer):
#     # Retrieve the last delivery date for the customer
#     last_delivery_date = DiffBottlesModel.objects.filter(customer=customer).aggregate(Max('delivery_date'))['delivery_date__max']

#     if last_delivery_date:
#         # Calculate the next delivery date
#         next_delivery_date = last_delivery_date + timedelta(days=7)  # Assuming a weekly delivery schedule
#     else:
#         # If there are no previous delivery dates, start from today
#         next_delivery_date = datetime.now().date()

#     return next_delivery_date


class NewRequestHome(View):
    template_name = 'customer_care/new_request_home.html'
    form_class = DiffBottles_Create_Form
    current_year = date.today().year
    current_month = date.today().month
    
    def find_next_delivery_date(self, customer):
        last_delivery_date = DiffBottlesModel.objects.filter(customer=customer).aggregate(Max('delivery_date'))['delivery_date__max']
        if last_delivery_date:
            next_delivery_date = last_delivery_date + timedelta(days=7)  # Assuming a weekly delivery schedule
        else:
            next_delivery_date = datetime.now().date()
        return next_delivery_date

    def get(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customers.objects.get(customer_id=customer_id)
            next_delivery_date = self.find_next_delivery_date(customer)
            
            # Find the last delivered date
            last_delivered_date = DiffBottlesModel.objects.filter(customer=customer).aggregate(Max('delivery_date'))['delivery_date__max']
            
            initial_data = {'delivery_date': next_delivery_date, 'mode': 'paid'}
            if customer and customer.sales_staff:
                initial_data['assign_this_to'] = customer.sales_staff  # Assign the user object
            else:
                initial_data['assign_this_to'] = None  # Default to None if no salesman is assigned
            form = self.form_class(initial=initial_data)
            # print("customer.sales_staff", customer.sales_staff)
            form = self.form_class(initial=initial_data)

            context = {
                'customer': customer,
                'username': customer.customer_name,
                'building_name': customer.building_name,
                'mobile_no': customer.mobile_no,
                'customer_type': customer.customer_type,
                'door_house_no': customer.door_house_no,
                'email_id': customer.email_id,
                'sales_man_name': customer.sales_staff.username if customer.sales_staff else "",
                'route': customer.routes.route_name if customer.routes else "",
                'next_delivery_date': next_delivery_date,
                'last_delivered_date': last_delivered_date,  # Add last delivered date to context
                'form': form,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            print(e)
            return render(request, self.template_name) 

    # def post(self, request, customer_id, *args, **kwargs):
    #     try:
    #         customer = Customers.objects.get(customer_id=customer_id)

    #         next_delivery_date = self.find_next_delivery_date(customer)

    #         form = self.form_class(request.POST, request.FILES)
    #         print(request.POST.get("request_type"))
    #         if form.is_valid():
    #             print(form)
    #             data = form.save(commit=False)
    #             data.customer = customer
    #             data.created_by = str(request.user.id)
    #             data.status = 'pending'
        
    #             data.save()

    #             # Send notification to the sales staff if assigned
    #             if customer.sales_staff:
    #                 sales_man = customer.sales_staff
    #                 print(sales_man,'sales_man')
    #                 notification_customer(sales_man.pk, "New Request", "A new request has been created.", "Sanawatercustomer")

    #             messages.success(request, 'Bottles Successfully Added.', 'alert-success')
    #             return redirect('requestType')
    #         else:
    #             messages.error(request, 'Form data is not valid.', 'alert-danger')
    #             context = {'form': form}
    #             return render(request, self.template_name, context)
    #     except Customers.DoesNotExist:
    #         messages.error(request, 'Customer does not exist.', 'alert-danger')
    #         return render(request, self.template_name)
    def post(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customers.objects.get(customer_id=customer_id)

            next_delivery_date = self.find_next_delivery_date(customer)

            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.customer = customer
                data.created_by = str(request.user.id)
                data.status = 'pending'
        
                data.save()

                # Send notification to the sales staff if assigned
                if customer.sales_staff:
                    sales_man = customer.sales_staff
                    try:
                        salesman_body = f'A new request has been created. for {customer.customer_name}'
                        notification(sales_man.pk, "New Water Request", salesman_body, "sanawater")
                        notification(customer.user_id.pk, "New Water Request", "Your Request Created Succesfull.", "sanawater")
                    except CustomUser.DoesNotExist:
                        messages.error(request, 'Salesman does not exist.', 'alert-danger')
                    except Send_Notification.DoesNotExist:
                        messages.error(request, 'No device token found for the salesman.', 'alert-danger')
                    except Exception as e:
                        messages.error(request, f'Error sending notification: {e}', 'alert-danger')

                messages.success(request, 'Bottles Successfully Added.', 'alert-success')
                return redirect('requestType')
            else:
                messages.error(request, 'Form data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Customers.DoesNotExist:
            messages.error(request, 'Customer does not exist.', 'alert-danger')
            return render(request, self.template_name)


class WaterDeliveryStatus(View):
    template_name = 'customer_care/water_delivery_status.html'

    def get(self, request, *args, **kwargs):
        form = DiffBottlesFilterForm(request.GET)
        queryset = form.filter_data() if form.is_valid() else DiffBottlesModel.objects.none()
        
        statustab = "pending"
        if request.GET.get('statustab') == "cancelled" :
            queryset = queryset.filter(status="cancelled")
            statustab = "cancelled"
        if request.GET.get('statustab') == "pending" :
            queryset = queryset.filter(status="pending")
            statustab = "pending"
        if request.GET.get('statustab') == "supplied" :
            queryset = queryset.filter(status="supplied")
            statustab = "supplied"
            

        context = {
            'form': form,
            'bottles_data': queryset,
            'statustab' : statustab
        }
        return render(request, self.template_name, context)
    
    

class EditQuantityView(View):
    def post(self, request, diffbottles_id):
        quantity = request.POST.get('quantity')
        diff_bottle = DiffBottlesModel.objects.get(diffbottles_id=diffbottles_id)
        diff_bottle.quantity_required = quantity
        diff_bottle.save()
        return HttpResponseRedirect(reverse('water_delivery_status')) 


class CancelRequestView(View):
    def get(self, request, diffbottles_id):
        if request.method == 'GET':
            diff_bottle = get_object_or_404(DiffBottlesModel, diffbottles_id=diffbottles_id)
            diff_bottle.status = 'Cancelled'
            diff_bottle.save()
        return redirect('new_request_home', customer_id=diff_bottle.customer.customer_id)


class ReassignRequestView(View):
    def get(self, request, diffbottles_id):
        diff_bottle = DiffBottlesModel.objects.filter(diffbottles_id=diffbottles_id).first()
        assign_this_to = diff_bottle.assign_this_to
        customer_id = diff_bottle.customer_id  # Retrieve the customer ID from the DiffBottlesModel instance
        salesmen = CustomUser.objects.filter(user_type='Salesman')
        print(salesmen,"salesmen")
        if assign_this_to:
            user_type = assign_this_to.user_type
            print("User Type:", user_type)
        else:
            print("No CustomUser assigned to this DiffBottlesModel.")
            user_type = None
        context = {
            'user_type': user_type,
            'salesmen': salesmen,
            'customer_id': customer_id,
            'diff_bottle': diff_bottle,  # Add customer ID to the context
        }
        return render(request, 'customer_care/reassign_request_form.html', context)

    def post(self, request, diffbottles_id):
        diff_bottle = DiffBottlesModel.objects.filter(diffbottles_id=diffbottles_id).first()
        print(diff_bottle.customer.sales_staff)
        assign_this_to_username_id = request.POST.get('assign_this_to')
        delivery_date = request.POST.get('delivery_date')     
        customuser=CustomUser.objects.get(id=assign_this_to_username_id)
        print("CUSTOMEUSER ::\n",customuser)

        if not assign_this_to_username_id:
            print("No CustomUser assigned. Cannot update.")
            # You can handle this case as required, such as returning an error message
            return HttpResponse("No CustomUser assigned. Cannot update.")

        diff_bottle.delivery_date = delivery_date
        diff_bottle.save()
        customer = diff_bottle.customer
        customer.sales_staff = customuser
        customer.save()
        print("DATA SAVED")     
        context = {
            'diff_bottle': diff_bottle,
        }
        return render(request, 'customer_care/reassign_request_form.html', context)

def new_registered_customers(request):
    # Fetch filters from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status_filter = request.GET.get('status')
    location_filter = request.GET.get('location')
    query = request.GET.get('q')

    # Query the CustomerRegistrationRequest model
    requests = CustomerRegistrationRequest.objects.all().order_by('-created_date')
    print("requests",requests)
    if start_date and end_date:
        requests = requests.filter(created_date__range=(start_date,end_date))

    if status_filter:
        requests = requests.filter(status=status_filter)
    if location_filter:
        requests = requests.filter(location_id=location_filter)
        
    if query:
        requests = requests.filter(
            Q(name__icontains=query) |
            Q(phone_no__icontains=query) |
            Q(building_name__icontains=query) |
            Q(room_or_flat_no__icontains=query) |
            Q(floor_no__icontains=query) |
            Q(email_id__icontains=query) |
            Q(no_of_5g_bottles_required__icontains=query) |
            Q(visit_schedule__icontains=query) |
            Q(status__icontains=query) |
            Q(location__location_name__icontains=query) |
            Q(emirate__name__icontains=query)
        )
    

    # Fetch data for filters
    emirates = EmirateMaster.objects.all()
    locations = LocationMaster.objects.all()
    log_activity(
            created_by=request.user,
            description=f"Viewed Newly Registered customer list with filters: Start Date = {start_date}, End Date = {end_date}, Status = {status_filter}, Location = {location_filter}, Query = {query}"
        )

    context = {
        'requests': requests,
        'emirates': emirates,
        'locations': locations,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'filter_data': {
            'start_date': start_date,
            'end_date': end_date,
            'q': query,

        },
    }
    return render(request, 'customer_care/new_registered_customers.html', context)


class CustomerRequestType_List(View):
    template_name = 'customer_care/customer_requesttype_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        request_li = CustomerRequestType.objects.all()
        context = {'request_li': request_li}
        return render(request, self.template_name, context)
    
class CustomerRequestType_Create(View):
    template_name = 'customer_care/customerrequesttype_create.html'
    form_class = CustomerRequestTypeForm

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            messages.success(request, 'Customer Request Successfully Added.', 'alert-success')
            return redirect('customer_request_type_list')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)
class CustomerRequestType_Edit(View):
    template_name = 'customer_care/customer_requesttype_edit.html'
    form_class = CustomerRequestType_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = CustomerRequestType.objects.get(id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = CustomerRequestType.objects.get(id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Request Data Successfully Updated', 'alert-success')
            return redirect('customer_request_type_list')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class CustomerRequestType_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(CustomerRequestType, id=pk)
        rec.delete()
        messages.success(request, 'Request type deleted successfully', 'alert-success')
        return redirect('customer_request_type_list')

    def post(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(CustomerRequestType, id=pk)
        rec.delete()
        messages.success(request, 'Request type deleted successfully', 'alert-success')
        return redirect('customer_request_type_list')
    
from django.utils import timezone    
class GuestCustomerList(View):
    template_name = 'customer_care/guest_customer_list.html'

    def get(self, request, *args, **kwargs):
        filter_data = {}

        query = request.GET.get("q")
        created_date_filter = request.GET.get('created_date')
        location_filter = request.GET.get('location')
        

        user_li = Customers.objects.filter(is_guest=True, is_deleted=False).select_related('location', 'routes')

        if query:
            user_li = user_li.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(whats_app__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )
            filter_data['q'] = query

        
        if created_date_filter:
            try:
                created_date_obj = datetime.strptime(created_date_filter, '%Y-%m-%d')
                created_date_obj = timezone.make_aware(created_date_obj, timezone.get_current_timezone())
                user_li = user_li.filter(created_date__date=created_date_obj.date())
                filter_data['created_date'] = created_date_filter
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

        if location_filter:
            user_li = user_li.filter(location__location_id=location_filter)
            filter_data['location'] = location_filter

        
        route_li = RouteMaster.objects.all()
        locations = LocationMaster.objects.all()

        log_activity(
            created_by=request.user,
            description=f"Viewed guest customer list with filters: {filter_data}"
        )

        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'filter_data': filter_data,
            'locations': locations,
        }
        return render(request, self.template_name, context)
    
    
class EditGuestCustomerView(View):
    template_name = "customer_care/edit_guest_customer.html"

    @method_decorator(login_required)
    def get(self, request, pk):
        branch = request.user.branch_id
        print("branch",branch)
        customer = get_object_or_404(Customers, pk=pk, is_guest=True, is_deleted=False)
        form = CustomerForm(branch,instance=customer)
        return render(request, self.template_name, {"form": form, "customer": customer})
    
    @method_decorator(login_required)
    def post(self, request, pk):
        branch = request.user.branch_id
        customer = get_object_or_404(Customers, pk=pk, is_guest=True, is_deleted=False)
        form = CustomerForm(branch,request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.is_guest = False 
            customer.save()
            messages.success(request, f"{customer.customer_name} has been assigned as a regular customer.")
            return redirect("guest_customers")
        return render(request, self.template_name, {"form": form, "customer": customer})
    

class GuestCustomerOrders(View):
    template_name = 'customer_care/guest_customer_orders.html'

    def get(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customers.objects.get(pk=customer_id, is_guest=True, is_deleted=False)
            orders = GuestCustomerOrder.objects.filter(customer=customer).order_by('-created_date')

            context = {
                'customer': customer,
                'orders': orders
            }
            return render(request, self.template_name, context)
        except Customers.DoesNotExist:
            messages.error(request, "Guest customer not found.")
            return redirect('guest_customers')
        
        
class ApproveGuestOrder(View):
    def get(self, request, order_id, *args, **kwargs):
        guest_order = get_object_or_404(GuestCustomerOrder, id=order_id)
        customer = guest_order.customer

        try:
            product_item = ProdutItemMaster.objects.get(product_name="5 Gallon")
            emergency_order = DiffBottlesModel.objects.create(
                customer=customer,
                product_item=product_item,
                quantity_required=guest_order.no_bottles_required,
                delivery_date=datetime.now().date(), 
                assign_this_to=customer.sales_staff,
                status="pending"
            )

            if customer.sales_staff:
                salesman_body = f"Emergency order approved for {customer.customer_name}"
                notification(customer.sales_staff.pk, "Emergency Order", salesman_body, "sanawater")
                notification(customer.user_id.pk, "Emergency Order", "Your emergency order has been approved.", "sanawater")

            messages.success(request, f"Emergency order created for {customer.customer_name}.", 'alert-success')
        except Exception as e:
            messages.error(request, f"Error creating emergency order: {e}", 'alert-danger')

        return redirect('guest_customers')