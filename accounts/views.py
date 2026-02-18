import uuid
import json
import base64
import datetime
import qrcode
from io import BytesIO
import base64

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.contrib.auth.hashers import is_password_usable

from competitor_analysis.forms import CompetitorAnalysisFilterForm
from master.functions import generate_form_errors, get_custom_id, log_activity
from van_management.views import find_customers
from .forms import *
from .models import *
from django.db.models import Q
import pandas as pd
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from client_management.models import *
from django.db.models import Q, Sum, Count
from customer_care.models import *
from van_management.models import Van_Routes,Van,VanProductStock

from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomPasswordChangeForm

# Create your views here.
@csrf_exempt
def move_schedule_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date = data.get('date')
        customers = data.get('customers')
        
        for customer_id in customers:
            customer_instance = Customers.objects.get(pk=customer_id)
            product_instance = ProdutItemMaster.objects.get(product_name="5 Gallon")
            
            if not DiffBottlesModel.objects.filter(product_item=product_instance,customer=customer_instance,delivery_date=date).exists():
                DiffBottlesModel.objects.create(
                    product_item=product_instance,
                    quantity_required=customer_instance.no_of_bottles_required,
                    delivery_date=date,
                    assign_this_to=customer_instance.sales_staff,
                    mode="paid",
                    amount=customer_instance.no_of_bottles_required * customer_instance.get_water_rate(),
                    discount_net_total=customer_instance.no_of_bottles_required * customer_instance.get_water_rate(),
                    created_by=request.user.id,
                    created_date=datetime.today(),
                    customer=customer_instance,
                )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
    

def user_login(request):
    template_name = 'registration/user_login.html'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Ensure fields are not empty
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, template_name)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                log_activity(
                    created_by=username,
                    description=f"User {username} logged in successfully."
                )
                return redirect('dashboard')
            else:
                messages.error(request, "Your account is inactive. Contact admin.")
                log_activity(
                    created_by=username,
                    description=f"User {username} attempted login but account is inactive."
                )
        else:
            messages.error(request, "Invalid username or password.")
            log_activity(
                created_by=username,
                description=f"Failed login attempt for username: {username}."
            )

    return render(request, template_name)   

class UserLogout(View):

    def get(self, request):
        try: 
            user = request.user
            username = user.username if user.is_authenticated else 'Unknown User'
            
            logout(request)
            messages.success(request, 'Successfully logged out', extra_tags='success')
            log_activity(
                created_by=username,
                description=f"User {username} logged out successfully."
            )
            return redirect("login")
        except Exception as e:
            log_activity(
                created_by=username,
                description=f"An error occurred while {username} was trying to log out: {str(e)}"
            )
            messages.error(request, 'An error occurred while logging out', extra_tags='danger')
            return redirect("login")
        
class Users_List(View):
    
    template_name = 'accounts/user_list.html'  

    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.exclude(user_type__in=[ 'Customers','Customer','customers','customer'])
        
        user = request.user
        username = user.username if user.is_authenticated else 'Unknown User'
        log_activity(
                created_by=username,
                description=f"User {username} accessed the Users List."
            )
        
        context = {
            'instances': users
        }
        return render(request, self.template_name, context)
    # template_name = 'accounts/user_list.html'
    
    # def get(self, request, *args, **kwargs):
    #     query = request.GET.get("q")
    #     user = request.user
    #     username = user.username if user.is_authenticated else 'Unknown User'
    #     instances = CustomUser.objects.all().exclude(user_type__in=['Customers','Customer','customers','customer'])
    #     if query:
    #         instances = instances.filter(
    #             Q(first_name__icontains=query) |
    #             Q(designation_id__designation_name__icontains=query) |
    #             Q(staff_id__icontains=query) |
    #             Q(username__icontains=query) |
    #             Q(branch_id__name__icontains=query) 
    #         )
    #         log_activity(
    #             created_by=username,
    #             description=f"User {username} performed a search in Users List with query: '{query}'."
    #         )
    #     else:
    #         # Log accessing the users list without search
    #         log_activity(
    #             created_by=username,
    #             description=f"User {username} accessed the Users List."
    #         )
    #     context = {
    #         'instances': instances,
    #         'q': query
    #         }
    #     return render(request, self.template_name, context)

class User_Create(View):
    template_name = 'accounts/user_create.html'
    form_class = User_Create_Form

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            passw = make_password(data.password)
            data.password = passw
            data.save()
            
            log_activity(
                created_by=request.user.username,
                description=f"User {data.username} created successfully by {request.user.username}."
            )
            
            messages.success(request, 'User Successfully Added.', 'alert-success')
            return redirect('users')
        else:
            log_activity(
                created_by=request.user.username,
                description=f"User creation failed due to form validation errors by {request.user.username}."
            )
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)


class User_Edit(View):
    template_name = 'accounts/user_edit.html'
    form_class = User_Edit_Form

    def get(self, request, pk, *args, **kwargs):
        rec = CustomUser.objects.get(id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        rec = CustomUser.objects.get(id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            #data.modified_by = request.user
            data.modified_date = datetime.now()
            data.save()
            
            log_activity(
                created_by=request.user.username,
                description=f"User {data.username} was updated successfully by {request.user.username}."
            )
            
            messages.success(request, 'User Data Successfully Updated', 'alert-success')
            return redirect('users')
        else:
            log_activity(
                created_by=request.user.username,
                description=f"User update failed for {rec.username} due to form validation errors by {request.user.username}."
            )
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class User_Details(View):
    template_name = 'accounts/user_details.html'

    def get(self, request, pk, *args, **kwargs):
        user_det = CustomUser.objects.get(id=pk)
        context = {'user_det': user_det}
        log_activity(
            created_by=request.user.username,
            description=f"User details for {user_det.username} were viewed by {request.user.username}."
        )
        return render(request, self.template_name, context)  
    
class User_Delete(View):
    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=pk)
        return render(request, 'accounts/user_delete.html', {'user': user})

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=pk)
        user.delete()
        log_activity(
            created_by=request.user.username,
            description=f"User {request.user.username} was deleted by {request.user.username}."
        )
        messages.success(request, 'User Successfully Deleted.', 'alert-success')
        return redirect('users')
# class Customer_List(View):
#     template_name = 'accounts/customer_list.html'

#     def get(self, request, *args, **kwargs):
#         # Create an instance of the form and populate it with GET data
#         form = CompetitorAnalysisFilterForm(request.GET)
        
#         user_li = Customers.objects.all()
#         query = request.GET.get("q")
#         if query:
#             user_li = user_li.filter(
#                 Q(customer_name__icontains=query) |
#                 Q(mobile_no__icontains=query) |
#                 Q(routes__route_name__icontains=query) |
#                 Q(location__location_name__icontains=query)|
#                 Q(building_name__icontains=query)
#             )

#         # Check if the form is valid
#         # if form.is_valid():
#             # Filter the queryset based on the form data
#         route_filter = request.GET.get('route_name')
#         if route_filter :
#             user_li = Customers.objects.filter(is_guest=False, routes__route_name=route_filter)
#         # else:
#         #         user_li = Customers.objects.all()
#         # else:
#         #     # If the form is not valid, retrieve all customers
#         #     user_li = Customers.objects.all()
#         route_li = RouteMaster.objects.all()
#         context = {'user_li': user_li, 'form': form, 'route_li': route_li}
#         return render(request, self.template_name, context)

# class Customer_List(View):
#     template_name = 'accounts/customer_list.html'

#     def get_next_visit_date(self, customer):
#         try:
#             staff_day_of_visit = Staff_Day_of_Visit.objects.get(customer=customer)
#             # Logic to determine the next visit date based on the visit schedule
#             # For demonstration purposes, let's assume the next visit is 7 days from today
#             next_visit_date = timezone.now() + timezone.timedelta(days=7)
#             return next_visit_date
#         except Staff_Day_of_Visit.DoesNotExist:
#             # Handle the case where no staff day of visit is found
#             return None

#     def get(self, request, *args, **kwargs):
#         # Retrieve the query parameter
#         query = request.GET.get("q")
#         route_filter = request.GET.get('route_name')
#         # Start with all customers
#         user_li = Customers.objects.all()

#         # Apply filters if they exist
#         if query:
#             user_li = user_li.filter(
#                 Q(custom_id__icontains=query) |
#                 Q(customer_name__icontains=query) |
#                 Q(mobile_no__icontains=query) |
#                 Q(routes__route_name__icontains=query) |
#                 Q(location__location_name__icontains=query) |
#                 Q(building_name__icontains=query)
#             )

#         if route_filter:
#             user_li = user_li.filter(routes__route_name=route_filter)

#         # Get all route names for the dropdown
#         route_li = RouteMaster.objects.all()

#         # Iterate over each customer and get the next visit date
#         for customer in user_li:
#             next_visit_date = self.get_next_visit_date(customer)
#             customer.next_visit_date = next_visit_date  # Add the next visit date to the customer object

#         context = {
#             'user_li': user_li.order_by("-created_date"), 
#             'route_li': route_li,
#             'route_filter': route_filter,
#             'q': query,
#         }
#         return render(request, self.template_name, context)
class Customer_List(View):
    template_name = 'accounts/customer_list.html'

    def get(self, request, *args, **kwargs):
        filter_data = {}

        # Retrieve query parameters
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        customer_type_filter = request.GET.get('customer_type')
        non_visit_reason = request.GET.get('non_visited_reason')
        created_date_filter = request.GET.get('created_date')
        location_filter = request.GET.get('location')  
        status_filter = request.GET.get('status')

        # Start with all customers
        user_li = Customers.objects.filter(is_guest=False, is_deleted=False).select_related('location', 'routes')

        # Apply filters
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

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)
            filter_data['route_filter'] = route_filter

        if customer_type_filter:
            user_li = user_li.filter(sales_type=customer_type_filter)
            filter_data['customer_type'] = customer_type_filter

        if created_date_filter:
            try:
                created_date_obj = datetime.strptime(created_date_filter, '%Y-%m-%d')
                created_date_obj = timezone.make_aware(created_date_obj, timezone.get_current_timezone())
                user_li = user_li.filter(created_date__date=created_date_obj.date())
                filter_data['created_date'] = created_date_filter
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

        if non_visit_reason:
            customer_ids = NonvisitReport.objects.filter(reason__id=non_visit_reason).values_list('customer_id', flat=True)
            user_li = user_li.filter(customer_id__in=customer_ids)
            filter_data['non_visit_reason'] = non_visit_reason

        if location_filter:
            user_li = user_li.filter(location__location_id=location_filter)
            filter_data['location'] = location_filter

        if status_filter:
            if status_filter == "active":
                user_li = user_li.filter(is_active=True)
            elif status_filter == "inactive":
                user_li = user_li.filter(is_active=False)
            filter_data['status'] = status_filter
        else:
            # default to active customers
            user_li = user_li.filter(is_active=True)
            
        # Get dropdown lists
        route_li = RouteMaster.objects.all()
        non_visit_reasons = NonVisitReason.objects.all()
        locations = LocationMaster.objects.all()  

        log_activity(
            created_by=request.user, 
            description=f"Viewed customer list with filters: {filter_data}"
        )

        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'route_filter': route_filter,
            'q': query,
            'filter_data': filter_data,
            'non_visit_reasons': non_visit_reasons,
            'locations': locations, 
            'status_filter': status_filter,
        }

        return render(request, self.template_name, context)
    # def get(self, request, *args, **kwargs):
    #     filter_data = {}
    #     # Retrieve the query parameter
    #     query = request.GET.get("q")
    #     route_filter = request.GET.get('route_name')
    #     customer_type_filter = request.GET.get('customer_type')
    #     non_visit_reason = request.GET.get('non_visited_reason')
    #     created_date_filter = request.GET.get('created_date', None)

    #     # Start with all customers
    #     user_li = Customers.objects.all().filter(is_deleted=False)
            
    #     # Apply filters if they exist
    #     if query:
    #         user_li = user_li.filter(
    #             Q(custom_id__icontains=query) |
    #             Q(customer_name__icontains=query) |
    #             Q(mobile_no__icontains=query) |
    #             Q(location__location_name__icontains=query) |
    #             Q(building_name__icontains=query)
    #         )
    #         filter_data['q'] = query

    #     if route_filter:
    #         user_li = user_li.filter(routes__route_name=route_filter)
    #         filter_data['route_filter'] = route_filter
            
    #     if customer_type_filter:
    #         user_li = user_li.filter(sales_type=customer_type_filter)
    #         filter_data['customer_type'] = customer_type_filter
    #     if created_date_filter:
    #         # Convert the string date to a datetime object
    #         created_date_obj = datetime.strptime(created_date_filter, '%Y-%m-%d')
            
    #         # Convert to a timezone-aware datetime object
    #         created_date_obj = timezone.make_aware(created_date_obj, timezone.get_current_timezone())
            
    #         # Filter users based on the created date (without time part)
    #         user_li = user_li.filter(created_date__date=created_date_obj.date())
            
    #         # Store the filter data to retain it in the template
    #         filter_data = {'created_date': created_date_filter}
    #     else:
    #         user_li = user_li.all()  # If no filter, return all users
    #         filter_data = {}
        
    #     if non_visit_reason:
    #         # Filter NonvisitReport by the selected reason
    #         customer_ids = NonvisitReport.objects.filter(reason__id=non_visit_reason).values_list('customer_id', flat=True)
            
    #         # Filter the main customer queryset
    #         user_li = user_li.filter(customer_id__in=customer_ids)
            
    #         # Update the filter_data dictionary
    #         filter_data['non_visit_reason'] = non_visit_reason

    #     # Get all route names for the dropdown
    #     route_li = RouteMaster.objects.all()
    #     non_visit_reasons = NonVisitReason.objects.all()

        
    #     log_activity(
    #         created_by=request.user, 
    #         description=f"Viewed customer list with filters: {filter_data}"
    #     )
    #     context = {
    #         'user_li': user_li.order_by("-created_date"),
    #         'route_li': route_li,
    #         'route_filter': route_filter,
    #         'q': query,
    #         'filter_data': filter_data,
    #         'non_visit_reasons':non_visit_reasons
    #     }



    #     return render(request, self.template_name, context)

def print_multiple_qrs(request):
    if request.method == 'POST':
        customer_ids = request.POST.getlist('customer_ids')
        customers = Customers.objects.filter(is_guest=False, pk__in=customer_ids)

        qr_data_list = []
        for customer in customers:
            data = f"{customer.pk}"
            qr = qrcode.make(data)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            qr_data_list.append({
                'id': customer.custom_id,
                'name': customer.customer_name,
                'qr_image': f"data:image/png;base64,{qr_base64}"
            })

        return render(request, 'accounts/print_qr_multiple.html', {'qr_data_list': qr_data_list})

class Latest_Customer_List(View):
    template_name = 'accounts/latest_customer_list.html'

    def get(self, request, *args, **kwargs):
        filter_data = {}
        
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        customer_type_filter = request.GET.get('customer_type')

        ten_days_ago = datetime.now() - timedelta(days=10)
        user_li = Customers.objects.filter(is_guest=False, created_date__gte=ten_days_ago,is_deleted=False)
        
        if request.GET.get('start_date'):
            start_date = request.GET.get('start_date')
        else:
            start_date = datetime.today().date()
            
        if request.GET.get('end_date'):
            end_date = request.GET.get('end_date')
        else:
            end_date = datetime.today().date()
        
        start_date = datetime.strptime(str(start_date), '%Y-%m-%d').date()   
        end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()
        
        filter_data["start_date"] = start_date.strftime('%Y-%m-%d') if start_date else None
        filter_data["end_date"] = end_date.strftime('%Y-%m-%d') if end_date else None
        
        user_li = user_li.filter(Q(created_date__date__range=[start_date, end_date]))
        
        if customer_type_filter:
            user_li = user_li.filter(sales_type=customer_type_filter)
            filter_data['customer_type'] = customer_type_filter

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)

        if query and query != "None":
            user_li = user_li.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )
            filter_data['q'] = query

        route_li = RouteMaster.objects.all()
        
        log_activity(
            created_by=request.user,  
            description=f"Viewed latest customer list with filters: {filter_data}"
        )
        
        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'route_filter': route_filter,
            'q': query,
        }

        return render(request, self.template_name, context)

class Inactive_Customer_List(View):
    template_name = 'accounts/inactive_customer_list.html'

    def get(self, request, *args, **kwargs):
        days_filter = request.GET.get('days_filter')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        route_name = request.GET.get('route_name')
        query = request.GET.get("q", "").strip().lower()
        filter_data = {}
        inactive_customers = Customers.objects.none() 

        today = timezone.now().date()

        if days_filter and days_filter != 'custom':
            to_date = today
            from_date = today - timedelta(days=int(days_filter))
            filter_data.update(days_filter=days_filter, from_date=from_date, to_date=to_date)
        else:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date() if from_date else today
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else today
            filter_data.update(days_filter='custom', from_date=from_date, to_date=to_date)

        if route_name:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            if van_route:
                salesman_id = van_route.van.salesman.pk
                filter_data['route_name'] = route_name

                visited_customers = CustomerSupply.objects.filter(
                    salesman_id=salesman_id,
                    created_date__date__range=(from_date, to_date)
                ).values_list('customer_id', flat=True)

                route_customers = Customers.objects.filter(is_guest=False, routes=van_route.routes,is_deleted=False,is_active=True)
                
                todays_customers = find_customers(request, str(today), van_route.routes.pk) or []
                todays_customer_ids = {customer['customer_id'] for customer in todays_customers}

                inactive_customers = route_customers.exclude(pk__in=visited_customers).exclude(pk__in=todays_customer_ids)

        if query:
            inactive_customers = inactive_customers.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(building_name__icontains=query)
            )
            filter_data['q'] = query

        def get_days_since_last_supply(customer_id):
            last_supply = CustomerSupply.objects.filter(customer_id=customer_id).order_by('-created_date').first()
            if last_supply:
                last_supply_date = last_supply.created_date.date()
                return last_supply_date, (today - last_supply_date).days
            return None, 0

        def check_vacation_status(customer_id):
            return Vacation.objects.filter(customer_id=customer_id, start_date__lte=today, end_date__gte=today).exists()

        filtered_customers = []
        for customer in inactive_customers:
            last_supply_date, days_since = get_days_since_last_supply(customer.pk)
            if days_since > 0:
                customer.last_supply_date = last_supply_date
                customer.days_since_last_supply = days_since
                customer.on_vacation = check_vacation_status(customer.pk)
                filtered_customers.append(customer)

        log_activity(
            created_by=request.user,
            description=f"Viewed inactive customer list with filters: {filter_data}"
        )

        context = {
            'inactive_customers': filtered_customers,
            'routes_instances': RouteMaster.objects.all(),
            'filter_data': filter_data,
            'data_filter': bool(route_name),
            'q': query,
            'today': today
        }

        return render(request, self.template_name, context)


class PrintInactiveCustomerList(View):
    template_name = 'accounts/print_inactive_customer_list.html'

    def get(self, request, *args, **kwargs):
        # Retrieve filters from GET parameters
        days_filter = request.GET.get('days_filter')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        route_name = request.GET.get('route_name')
        query = request.GET.get("q", "").strip().lower()
        filter_data = {}

        # Define today's date
        today = timezone.now().date()

        # Handle days filter or custom date range
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%b. %d, %Y').date()
                except ValueError:
                    return today  # Default to today if parsing fails

        if days_filter and days_filter != 'custom':
            to_date = today
            from_date = today - timedelta(days=int(days_filter))
            filter_data.update(days_filter=days_filter, from_date=from_date, to_date=to_date)
        else:
            from_date = parse_date(from_date) if from_date else today
            to_date = parse_date(to_date) if to_date else today
            filter_data.update(days_filter='custom', from_date=from_date, to_date=to_date)


        # Initialize inactive_customers as an empty queryset
        inactive_customers = Customers.objects.none()

        # Filter by route if specified
        if route_name:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            if van_route:
                salesman_id = van_route.van.salesman.pk
                filter_data['route_name'] = route_name

                # Retrieve customers visited within the date range and exclude today's customers
                visited_customers = CustomerSupply.objects.filter(
                    salesman_id=salesman_id,
                    created_date__date__range=(from_date, to_date)
                ).values_list('customer_id', flat=True)
                
                route_customers = Customers.objects.filter(is_guest=False, routes=van_route.routes,is_deleted=False,is_active=True)
                
                # Ensure `todays_customers` is an empty list if `find_customers` returns None
                todays_customers = find_customers(request, str(today), van_route.routes.pk) or []
                todays_customer_ids = {customer['customer_id'] for customer in todays_customers}

                # Exclude visited and today's customers
                inactive_customers = route_customers.exclude(pk__in=visited_customers).exclude(pk__in=todays_customer_ids)

        # Apply search query filter if present
        if query:
            inactive_customers = inactive_customers.filter(
                custom_id__icontains=query
            ) | inactive_customers.filter(
                customer_name__icontains=query
            ) | inactive_customers.filter(
                building_name__icontains=query
            )
            filter_data['q'] = query

        # Helper to get last supply date and days since last supply
        def get_days_since_last_supply(customer_id):
            last_supply = CustomerSupply.objects.filter(customer_id=customer_id).order_by('-created_date').first()
            if last_supply:
                last_supply_date = last_supply.created_date.date()
                return last_supply_date, (today - last_supply_date).days
            return None, 0

        # Helper to check vacation status
        def check_vacation_status(customer_id):
            return Vacation.objects.filter(customer_id=customer_id, start_date__lte=today, end_date__gte=today).exists()

        # Prepare data for each inactive customer
        filtered_customers = []
        for customer in inactive_customers:
            last_supply_date, days_since = get_days_since_last_supply(customer.pk)
            if days_since > 0:
                customer.last_supply_date = last_supply_date
                customer.days_since_last_supply = days_since
                customer.on_vacation = check_vacation_status(customer.pk)
                filtered_customers.append(customer)
        log_activity(
            created_by=request.user,
            description=f"Viewed inactive customer Print with filters: {filter_data}"
        )
        # Set context for rendering template
        context = {
            'inactive_customers': filtered_customers,
            'filter_data': filter_data,
            'today': today
        }
        return render(request, self.template_name, context)
    
class CustomerComplaintView(View):
    template_name = 'accounts/customer_complaint.html'

    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customers, customer_id=pk)
        complaints = CustomerComplaint.objects.filter(customer=customer)
        log_activity(
            created_by=request.user,  
            description=f"Viewed complaints for customer {customer.customer_id}"
        )
        return render(request, self.template_name, {'customer': customer, 'complaints': complaints})

    def post(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customers, customer_id=pk)
        complaint_id = request.POST.get('complaint_id')
        status = request.POST.get('status')
        complaint = get_object_or_404(CustomerComplaint, id=complaint_id, customer=customer)
        if status == "Completed":
            complaint.status = status
            complaint.save()
            log_activity(
                created_by=request.user,  
                description=f"Updated complaint {complaint_id} status to {status} for customer {customer.customer_id}"
            )
        return redirect('customer_complaint', pk=pk)


def create_customer(request):
    branch = request.user.branch_id
    template_name = 'accounts/create_customer.html'
    form = CustomercreateForm(branch)
    context = {"form":form}
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = CustomercreateForm(branch,data = request.POST)
                context = {"form":form}
                if form.is_valid():
                    mobile_no = form.cleaned_data.get("mobile_no")
                    customer_name = form.cleaned_data.get("customer_name")

                    if mobile_no:
                        hashed_password = make_password(mobile_no)

                        customer_user_data = CustomUser.objects.create(
                            password=hashed_password,
                            username=mobile_no,
                            first_name=customer_name,
                            user_type='Customer'
                        )
                    
                    data = form.save(commit=False)
                    data.created_by = str(request.user)
                    data.created_date = datetime.now()
                    data.emirate = data.location.emirate
                    branch_id = request.user.branch_id.branch_id
                    branch = BranchMaster.objects.get(branch_id=branch_id)
                    data.branch_id = branch
                    data.custom_id = get_custom_id(Customers)
                    if mobile_no:
                        data.user_id = customer_user_data
                    data.save()
                    Staff_Day_of_Visit.objects.create(customer = data)
                    
                    log_activity(
                        created_by=request.user,
                        description=f"Created customer {data.custom_id} - {data.customer_name}"
                    )
                    
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Customer Created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('customers')
                    }
                    
                else:
                    message = generate_form_errors(form, formset=False)
                    
                    response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": message,
                    }
                    
        except IntegrityError as e:
            log_activity(
                created_by=request.user,
                description=f"IntegrityError while creating customer {str(e)}"
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
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        return render(request, template_name,context)
        
def load_locations(request):
    emirate_id = request.GET.get('emirate_id')
    locations = LocationMaster.objects.filter(emirate__pk=emirate_id).all()
    log_activity(
            created_by=request.user if request.user.is_authenticated else None,
            description=f"Loaded locations for emirate_id {emirate_id}"
        )
    return JsonResponse(list(locations.values('location_id', 'location_name')), safe=False)

# class Customer_Details(View):
#     template_name = 'accounts/customer_details.html'

#     def get(self, request, pk, *args, **kwargs):
#         user_det = Customers.objects.get(customer_id=pk)
#         context = {'user_det': user_det}
#         return render(request, self.template_name, context) 

class Customer_Details(View):
    template_name = 'accounts/customer_details.html'

    def get(self, request, pk, *args, **kwargs):
        user_det = Customers.objects.get(customer_id=pk)
        visit_schedule = self.format_visit_schedule(user_det.visit_schedule)
        context = {'user_det': user_det, 'visit_schedule': visit_schedule}
        log_activity(
            created_by=request.user if request.user.is_authenticated else None,
            description=f"Viewed details for customer {user_det.customer_name}"
        )
        return render(request, self.template_name, context)

    def format_visit_schedule(self, visit_schedule):
        week_schedule = {}
        no_week_days = []
        formatted_schedule = []
        
        if visit_schedule:
            for day, weeks in visit_schedule.items():
                if weeks == ['']:
                    no_week_days.append(day)
                else:
                    for week in weeks:
                        if week not in week_schedule:
                            week_schedule[week] = []
                        week_schedule[week].append(day)
            
            
            if no_week_days:
                days = ', '.join(no_week_days)
                formatted_schedule.append(f"General: {days}")
            
            for week in sorted(week_schedule.keys(), reverse=True):
                days = ', '.join(week_schedule[week])
                formatted_schedule.append(f"{week}: {days}")
        return formatted_schedule

def edit_customer(request,pk):
    branch = request.user.branch_id
    cust_Data = Customers.objects.get(customer_id = pk,is_deleted=False)
    form = CustomerEditForm(branch,instance = cust_Data)
    template_name = 'accounts/edit_customer.html'
    context = {"form":form}
    try:
        if request.method == 'POST':
            form = CustomerEditForm(branch,instance = cust_Data,data = request.POST)
            context = {"form":form}
            previous_rate =cust_Data.rate

            if form.is_valid():
                # print("previous_rate",previous_rate)
                data = form.save(commit=False)
                data.emirate = data.location.emirate
                data.save()
                
                if not data.user_id:
                    mobile_no = form.cleaned_data.get("mobile_no")
                    customer_name = form.cleaned_data.get("customer_name")

                    if mobile_no:
                        hashed_password = make_password(mobile_no)

                        customer_user_data,new_user = CustomUser.objects.get_or_create(
                            username=mobile_no,
                            first_name=customer_name,
                            user_type='Customer'
                        )
                        if new_user:
                            new_user.password=hashed_password
                            new_user.save()
                            
                        data.user_id = customer_user_data
                        data.save()
                
                # Create CustomerRateHistory entry
                CustomerRateHistory.objects.create(
                    customer=cust_Data,
                    previous_rate=previous_rate,
                    new_rate=data.rate,
                    created_by=request.user
                    )
                messages.success(request, 'Customer Details Updated successfully!')
                log_activity(
                    created_by=request.user,
                    description=f"Updated details for customer {cust_Data.customer_name}"
                )
                return redirect('customers')
            else:
                messages.success(request, 'Invalid form data. Please check the input.')
                return render(request, template_name,context)
        return render(request, template_name,context)
    except Exception as e:
        print(":::::::::::::::::::::::",e)
        messages.success(request, 'Something went wrong')
        return render(request, template_name,context)
    
import random

def randomnumber(digits):
    """Generate a random number with the specified number of digits."""
    range_start = 10**(digits - 1)
    range_end = (10**digits) - 1
    return random.randint(range_start, range_end)

def delete_customer(request,pk):
    cust_Data = Customers.objects.get(customer_id=pk)
    cust_Data.is_deleted = True
    
    if cust_Data.user_id:
        user = cust_Data.user_id
        
        if not user.username.endswith("_deleted"):
            user.username += str(randomnumber(3)) + "_deleted"
        
        if user.email and not user.email.endswith("_deleted"):
            user.email += str(randomnumber(3)) + "_deleted"
            
        if user.phone and not user.phone.endswith("_deleted"):
            user.phone += str(randomnumber(3)) + "_deleted"
        
        user.save() 
    
    cust_Data.save()
    
    log_activity(
            created_by=request.user if request.user.is_authenticated else None,
            description=f"Deleted customer with ID {cust_Data.customer_name}"
        )
    
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Customer Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('customers'),
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')

from accounts.templatetags.accounts_templatetags import get_next_visit_day

def customer_list_excel(request):
    query = request.GET.get("q")
    route_filter = request.GET.get('route_name')

    # Optimize by selecting only required fields
    user_li = Customers.objects.filter(is_guest=False, is_deleted=False).select_related('routes', 'location')

    if query and query not in ('', 'None'):
        user_li = user_li.filter(
            Q(custom_id__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(mobile_no__icontains=query) |
            Q(routes__route_name__icontains=query) |
            Q(location__location_name__icontains=query) |
            Q(building_name__icontains=query)
        )

    if route_filter and route_filter not in ('', 'None'):
        user_li = user_li.filter(routes__route_name=route_filter)

    # Prefetch related data to reduce queries in loop
    custody_stock_data = {
        cs.customer_id: cs.quantity
        for cs in CustomerCustodyStock.objects.filter(product__product_name="5 Gallon")
    }
    
    outstanding_bottle_data = {
        co.customer_id: co.value
        for co in CustomerOutstandingReport.objects.filter(product_type="emptycan")
    }

    last_supplied_data = {
        ls.customer_supply.customer_id: ls.quantity
        for ls in CustomerSupplyItems.objects.select_related('customer_supply')
        .order_by('-customer_supply__created_date')
    }

    data = {
        'Serial Number': [],
        'Customer ID': [],
        'Customer name': [],
        'Route': [],
        'Location': [],
        'Mobile No': [],
        'Building Name': [],
        'House No': [],
        'Bottles stock': [],
        'Next Visit date': [],
        'Sales Type': [],
        'Rate': [],
    }

    for serial_number, customer in enumerate(user_li, start=1):
        next_visit_date = get_next_visit_day(customer.pk)

        custody_count = custody_stock_data.get(customer.pk, 0)
        outstanding_bottle_count = outstanding_bottle_data.get(customer.pk, 0)
        last_supplied_count = last_supplied_data.get(customer.pk, 0)

        total_bottle_count = custody_count + outstanding_bottle_count + last_supplied_count

        data['Serial Number'].append(serial_number)
        data['Customer ID'].append(customer.custom_id)
        data['Customer name'].append(customer.customer_name)
        data['Route'].append(customer.routes.route_name if customer.routes else '')
        data['Location'].append(customer.location.location_name if customer.location else '')
        data['Mobile No'].append(customer.mobile_no)
        data['Building Name'].append(customer.building_name)
        data['House No'].append(customer.door_house_no if customer.door_house_no else 'Nil')
        data['Bottles stock'].append(total_bottle_count)
        data['Next Visit date'].append(next_visit_date)
        data['Sales Type'].append(customer.sales_type)
        data['Rate'].append(customer.rate)

    df = pd.DataFrame(data)

    # Excel writing optimization
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=4)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        table_border_format = workbook.add_format({'border': 1})
        worksheet.conditional_format(4, 0, len(df.index) + 4, len(df.columns) - 1, 
                                     {'type': 'cell', 'criteria': '>', 'value': 0, 'format': table_border_format})
        
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 16, 'border': 1})
        worksheet.merge_range('A1:L2', f'Sana Water', merge_format)
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        worksheet.merge_range('A3:L3', f'    Customer List   ', merge_format)
        worksheet.merge_range('A4:L4', '', merge_format)

    filename = "Customer List.xlsx"
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    log_activity(
        created_by=request.user,
        description="Generated and downloaded customer list Excel report"
    )

    return response

# def visit_days_assign(request,customer_id):
#     template_name = 'accounts/assign_dayof_visit.html'
#     customer_data=Customers.objects.get(customer_id = customer_id)
#     day_visits = Staff_Day_of_Visit.objects.get(customer_id__customer_id = customer_id)
#     form = Day_OfVisit_Form(instance=day_visits)
#     context = {'day_visits' : day_visits,"form":form,"customer_data":customer_data}
#     if request.method == 'POST':
#         context = {'day_visits' : day_visits,"form":form,"customer_data":customer_data}
#         form = Day_OfVisit_Form(request.POST,instance=day_visits)
#         if form.is_valid():
#             data = form.save(commit=False)
#             data.created_by = str(request.user)
#             data.created_date = datetime.now()
#             data.save()
#             messages.success(request, 'Day of visit updated successfully!')
#             return redirect('customers')
#         else:
#             messages.success(request, 'Invalid form data. Please check the input.')
#             return render(request, template_name,context)
#     return render(request,template_name ,context)


# def visit_days_assign(request, customer_id):
#     template_name = 'accounts/assign_dayof_visit.html'
    
#     try:
#         customer_data = Customers.objects.get(customer_id=customer_id)
#         visit_schedule_data = customer_data.visit_schedule
        
#         if visit_schedule_data is not None:
#             if isinstance(visit_schedule_data, str):
#                 visit_schedule_data = json.loads(visit_schedule_data)
#                 print(visit_schedule_data)
#             else:
#                 print("Visit schedule data is already a dictionary.")
#                 # Handle the case where visit_schedule_data is already a dictionary
            
#         else:
#             print("Visit schedule data is None.")
#     except Customers.DoesNotExist:
#         messages.error(request, 'Customer does not exist.')
#         return redirect('customers')
    
#     if request.method == 'POST':
#         visit_schedule_data = {}
#         for week_number in "1234":
#             selected_days = []
#             for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
#                 checkbox_name = f'week{week_number}[]'
#                 if checkbox_name in request.POST:
#                     if day in request.POST.getlist(checkbox_name):
#                         selected_days.append(day)
#             visit_schedule_data["week" + week_number] = selected_days

#         # Convert the dictionary to JSON
#         visit_schedule_json = json.dumps(visit_schedule_data)

#         # Save the JSON data to the database field
#         customer_data.visit_schedule = visit_schedule_json
#         customer_data.save()

#         messages.success(request, 'Visit schedule updated successfully!')
#         return redirect('customers')
    
#     # Render the form if it's a GET request
#     context = {
#         "customer_data": customer_data,
#         "visit_schedule_data": visit_schedule_data
#     }
#     return render(request, template_name, context)


def visit_days_assign(request, customer_id):
    template_name = 'accounts/assign_dayof_visit.html'
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    try:
        customer_data = Customers.objects.get(customer_id=customer_id)
        visit_schedule_data = customer_data.visit_schedule

        if visit_schedule_data is not None:
            if isinstance(visit_schedule_data, str):
                visit_schedule_data = visit_schedule_data
        else:
            visit_schedule_data = {}  # Initialize an empty dictionary if it's None
            
        # print(visit_schedule_data)
        
    except Customers.DoesNotExist:
        messages.error(request, 'Customer does not exist.')
        return redirect('customers')
    
    if request.method == 'POST':
        # Initialize an empty dictionary to store the new visit schedule data
        visit_schedule_data = {day: [] for day in days_of_week}

        # Iterate over the days of the week and update the dictionary based on the POST data
        for week_number in "12345":
            week_key = f"Week{week_number}[]"
            selected_days = request.POST.getlist(week_key)
            for day in selected_days:
                visit_schedule_data[day].append(f"Week{week_number}")
                
        # Split the week strings into lists and ensure all weeks are individual elements
        for day in days_of_week:
            visit_schedule_data[day] = [
                week for weeks in visit_schedule_data[day]
                for week in weeks.split(',')
            ]
            
        # print(visit_schedule_data)

        # Save the JSON data to the database field
        customer_data.visit_schedule = visit_schedule_data
        customer_data.save()

        created_by = request.user.username  
        description = f"Updated visit schedule for customer {customer_id}"
        log_activity(created_by, description)
        
        messages.success(request, 'Visit schedule updated successfully!')
        return redirect('customers')
    
    # Render the form if it's a GET request
    context = {
        "customer_data": customer_data,
        "visit_schedule_data": visit_schedule_data,
        "days_of_week": days_of_week
    }
    return render(request, template_name, context)


class CustomerRateHistoryListView(View):
    template_name = 'accounts/customer_rate_history.html'

    def get(self, request, pk, *args, **kwargs):
        customer_instance = Customers.objects.get(pk=pk)
        customer_rate_instances = CustomerPriceChange.objects.filter(customer=customer_instance).order_by('-created_date')
        other_product_rate_instances = CustomerOtherProductChargesChanges.objects.filter(customer=customer_instance).order_by('-created_date')
        
        new_rate_form = CustomerPriceChangeForm()
        # Log the activity for viewing customer rate history
        log_activity(
            created_by=request.user,
            description=f"Viewed rate history for customer: {customer_instance.customer_name})"
        )
        
        context = {
            "customer_instance": customer_instance,
            "customer_rate_instances": customer_rate_instances,
            "other_product_rate_instances": other_product_rate_instances,
            "new_rate_form": new_rate_form,
            "product_items": ProdutItemMaster.objects.exclude(product_name="5 gallon")
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk, *args, **kwargs):
        customer_instance = Customers.objects.get(pk=pk)
        
        form = CustomerPriceChangeForm(data=request.POST)
        
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.old_price = customer_instance.rate
            data.customer = customer_instance
            data.save()
            
            customer_instance.rate=data.new_price
            customer_instance.save()
            # Log the activity for rate update
            log_activity(
                created_by=request.user,
                description=f"Updated rate for customer: {customer_instance.customer_name} (ID: {pk}) to {data.new_price}"
            )
            
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Rate Updated successfully.",
                'redirect': 'true',
                "redirect_url": reverse('customer_rate_history', kwargs={'pk': pk})
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            # Log the failed update attempt
            log_activity(
                created_by=request.user,
                description=f"Failed to update rate for customer: {customer_instance.customer_name} (ID: {pk}) due to invalid form data"
            )

            messages.error(request, 'Invalid form data. Please check the input.')
            
class OtherProductRateChangeView(View):
    def post(self, request, pk, *args, **kwargs):
        customer_instance = get_object_or_404(Customers, pk=pk)
        
        if not CustomerOtherProductCharges.objects.filter(customer=customer_instance).exists():
            product_items = ProdutItemMaster.objects.exclude(product_name="5 gallon")
            
            for product_item in product_items:
                current_rate = request.POST.get(str(product_item.pk))
                if not current_rate:
                    continue
                
                try:
                    current_rate = float(current_rate)  # Convert to appropriate type if needed
                except ValueError:
                    continue
                
                CustomerOtherProductChargesChanges.objects.create(
                    created_by=request.user,
                    customer=customer_instance,
                    product_item=product_item,
                    privious_rate=product_item.rate,
                    current_rate=current_rate
                )
                
                customer_charge, created = CustomerOtherProductCharges.objects.get_or_create(
                    customer=customer_instance,
                    product_item=product_item,
                )
                customer_charge.current_rate = current_rate
                customer_charge.save()
            
                log_activity(
                    created_by=request.user,
                    description=f"Updated rate for customer: {customer_instance.customer_name} (ID: {customer_instance.custom_id}) to {customer_charge.current_rate}"
                )
        else:
            
            product_item = ProdutItemMaster.objects.get(pk=request.POST.get("other_product_item"))
            current_rate = request.POST.get("other_product_item_value")
            current_rate = float(current_rate)
            
            CustomerOtherProductChargesChanges.objects.create(
                created_by=request.user,
                customer=customer_instance,
                product_item=product_item,
                privious_rate=product_item.rate,
                current_rate=current_rate
            )
            
            customer_charge, created = CustomerOtherProductCharges.objects.get_or_create(
                customer=customer_instance,
                product_item=product_item,
            )
            customer_charge.current_rate = current_rate
            customer_charge.save()
            
            log_activity(
                    created_by=request.user,
                    description=f"Updated rate for customer: {customer_instance.customer_name} (ID: {customer_instance.custom_id}) to {customer_charge.current_rate}"
                )
        
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Rate updated successfully.",
            'redirect': 'true',
            "redirect_url": reverse('customer_rate_history', kwargs={'pk': pk})
        }
        return JsonResponse(response_data)

def customer_username_change(request, customer_id):
    customer = get_object_or_404(Customers, customer_id=customer_id)

    # Case 1: user exists → instance will be pre-filled
    if customer.user_id:
        instance = customer.user_id
    else:
        instance = None  # empty form

    if request.method == "POST":
        form = ChangeUsernameForm(request.POST, instance=instance)
        if form.is_valid():
            user = form.save(commit=False)
            if not instance:
                user.save()
                customer.user_id = user
                customer.save()
            else:
                user.save()

            return JsonResponse({
                "status": "true",
                "message": "Username saved successfully.",
                "redirect_url": reverse('customers')
            })
        else:
            return JsonResponse({
                "status": "false",
                "message": form.errors.get("username", ["Form is invalid."])[0]
            })

    form = ChangeUsernameForm(instance=instance)
    return render(request, "accounts/customer_username_change.html", {
        "form": form,
        "customer": customer
    })

def customer_password_change(request, customer_id):
    customer = get_object_or_404(Customers, customer_id=customer_id)

    if not customer.user_id:
        return JsonResponse({
            "status": "false",
            "message": "No user linked to this customer."
        })

    user = customer.user_id

    if request.method == "POST":
        form = CustomerPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)
            return JsonResponse({
                "status": "true",
                "message": "Password updated successfully.",
                "redirect_url": reverse('customers')
            })
        else:
            return JsonResponse({
                "status": "false",
                "message": (
                    form.errors.get("new_password1", [""])[0]
                    or form.errors.get("new_password2", [""])[0]
                    or form.errors.get("__all__", ["Form is invalid."])[0]
                )
            })

    form = CustomPasswordChangeForm(user=user)
    has_password = is_password_usable(user.password)
    return render(request, "accounts/change_customer_password.html", {
        "form": form,
        "customer": customer,
        "has_password": has_password
    })

class NonVisitedCustomersView(View):
    template_name = 'accounts/non_visited_customers.html'
    paginate_by = 50  # Optional: For pagination, you can set this value

    def get(self, request, *args, **kwargs):
        # Get filter data from request
        date = request.GET.get('date')
        route_name = request.GET.get('route_name')
        query = request.GET.get("q")
        filter_data = {}
        non_visited = []

        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
            
        
        if route_name:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            if van_route:
                salesman_id = van_route.van.salesman.pk
                filter_data['route_name'] = route_name

                # Actual visit
                visited_customers = CustomerSupply.objects.filter(salesman_id=salesman_id, created_date__date=date)
                todays_customers = find_customers(request, str(date), van_route.routes.pk) or []

                # todays_customers = find_customers(request, str(date), van_route.routes.pk)
                # # Convert each dictionary to a tuple of items for hashing
                # planned_visit = set(tuple(customer.items()) for customer in todays_customers)
                # visited = set(visited_customers.values_list('customer_id', flat=True))
                # non_visited = list(planned_visit - visited)
                # Convert the data to dictionaries for easier processing
                todays_customers_dict = [dict(customer) for customer in todays_customers]
                visited_customers_ids = set(visited_customers.values_list('customer_id', flat=True))
                
                # Filter out visited customers
                non_visited = [customer for customer in todays_customers_dict if customer['customer_id'] not in visited_customers_ids]
        
        
        if query and query != "None":
            query = query.lower()
            # Ensure query is a string
            query_str = str(query)
            non_visited = [customer for customer in non_visited if (
                query_str in str(customer.get('custom_id', '')).lower() or
                query_str in str(customer.get('customer_name', '')).lower() or
                query_str in str(customer.get('mobile', '')).lower() or
                query_str in str(customer.get('location', '')).lower() or
                query_str in str(customer.get('building_name', '')).lower()
            )]
            filter_data['q'] = query
            
        log_activity(created_by= request.user.username, description= (f"Viewed non-visited customers with date: {filter_data['filter_date']} "
                       f"and route: {filter_data.get('route_name', 'All')}."))
        
        context = {
            'non_visited': non_visited,
            'routes_instances': RouteMaster.objects.all(),
            'filter_data': filter_data,
            'data_filter': bool(route_name),
            'q': query,
        }

        return render(request, self.template_name, context)   
    
 
def change_password(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  
            log_activity(
                created_by=request.user.username, 
                description=f"Password changed for user: {user.username}"
            )
            return redirect('password_change_done')
        else:
            log_activity(
                created_by=request.user.username, 
                description=f"Failed password change attempt for user: {user.username}. Errors: {form.errors}"
            )
    else:
        form = CustomPasswordChangeForm(user=user)

    return render(request, 'accounts/change_password.html', {'form': form})


class MissingCustomersView(View):
    template_name = 'accounts/missing_customers.html'

    def get(self, request, *args, **kwargs):
        filter_data = {}
        request_date = request.GET.get('date')
        
        if request_date:
            request_date = datetime.strptime(request_date, '%Y-%m-%d').date()
            filter_data['filter_date'] = request_date.strftime('%Y-%m-%d')
        else:
            request_date = datetime.now().date()
            filter_data['filter_date'] = request_date.strftime('%Y-%m-%d')

        routes = RouteMaster.objects.all()  # Get all RouteMaster instances
        # route_data = []

        # for route in routes:
        #     route_id = route.route_id  # Use route_id from RouteMaster
        #     actual_visitors = Customers.objects.filter(is_guest=False, routes__pk=route_id, is_active=True).count()

        #     planned_visitors_list = find_customers(request, str(date), route_id)  # Ensure this returns a list
        #     planned_visitors = len(planned_visitors_list) if planned_visitors_list else 0

        #     supplied_customers = CustomerSupply.objects.filter(
        #         customer__routes__pk=route_id,
        #         created_date__date=date
        #     ).count()

        #     if isinstance(planned_visitors_list, list):
        #         todays_customers_dict = planned_visitors_list
        #     else:
        #         todays_customers_dict = []

        #     visited_customers_ids = set(
        #         CustomerSupply.objects.filter(
        #             customer__routes__pk=route_id,
        #             created_date__date=date
        #         ).values_list('customer_id', flat=True)
        #     )

        #     # Filter out visited customers
        #     missed_customers = [
        #         customer for customer in todays_customers_dict 
        #         if customer['customer_id'] not in visited_customers_ids
        #     ]

        #     missed_customers_count = len(missed_customers)
        #     # print("missed_customers_count", missed_customers_count)

            # route_data.append({
            #     'route_name': route.route_name,  
            #     'actual_visitors': actual_visitors,
            #     'planned_visitors': planned_visitors,
            #     'missed_customers': missed_customers_count,
            #     'supplied_customers': supplied_customers,
            #     'route_id': route.route_id  
            # })

        # log_activity(
        #         created_by=request.user.username, 
        #         description=f"Processed route: {route.route_name}. Missed customers count: {missed_customers_count}"
        #     )
        
        context = {
            'route_data': routes,
            'filter_data': filter_data,
            'request_date': request_date
        }

        return render(request, self.template_name, context)

class MissingCustomersPdfView(View):
    template_name = 'accounts/missing_customers_pdf.html'

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()  

        routes = RouteMaster.objects.all()  
        route_data = []

        for route in routes:
            route_id = route.route_id
            actual_visitors = Customers.objects.filter(is_guest=False, routes__pk=route_id, is_active=True).count()

            planned_visitors_list = find_customers(request, str(date), route_id)  # Ensure this returns a list
            planned_visitors = len(planned_visitors_list) if planned_visitors_list else 0

            supplied_customers = CustomerSupply.objects.filter(
                customer__routes__pk=route_id,
                created_date__date=date
            ).count()

            if isinstance(planned_visitors_list, list):
                todays_customers_dict = planned_visitors_list
            else:
                todays_customers_dict = []

            visited_customers_ids = set(
                CustomerSupply.objects.filter(
                    customer__routes__pk=route_id,
                    created_date__date=date
                ).values_list('customer_id', flat=True)
            )

            missed_customers = [
                customer for customer in todays_customers_dict
                if customer['customer_id'] not in visited_customers_ids
            ]

            missed_customers_count = len(missed_customers)

            route_data.append({
                'route_name': route.route_name,
                'actual_visitors': actual_visitors,
                'planned_visitors': planned_visitors,
                'missed_customers': missed_customers_count,
                'supplied_customers': supplied_customers,
                'route_id': route.route_id
            })

        log_activity(
                created_by=request.user.username,
                description=f"Processed route: {route.route_name}. Missed customers count: {missed_customers_count}"
            )
        
        context = {
            'route_data': route_data
        }
        return render(request, self.template_name, context)


        
class MissedOnDeliveryView(View):
    template_name = 'accounts/missed_on_delivery.html'

    def get(self, request, route_id, *args, **kwargs):
        filter_data = {}
        request_date_str = request.GET.get('request_date')

        if request_date_str:
            # try:
            request_date = datetime.strptime(request_date_str, '%Y-%m-%d').date()
            # except ValueError:
                # request_date = datetime.now().date()
        else:
            request_date = datetime.now().date()

        filter_data['filter_date'] = request_date.strftime('%Y-%m-%d')
        
        planned_customers = find_customers(request, str(request_date), route_id) or []

        supplied_customers_ids = CustomerSupply.objects.filter(
            customer__routes__route_id=route_id,
            created_date__date=request_date
        ).values_list('customer_id', flat=True)

        missed_customers = []
        for customer in planned_customers:
            if customer['customer_id'] not in supplied_customers_ids:
                if (last_supply_instances:=CustomerSupply.objects.filter(customer_id=customer['customer_id'])).exists():
                    last_supply = last_supply_instances.latest('-created_date')

                    last_sold_date = last_supply.created_date if last_supply else None
                else:
                    last_sold_date = None

                # Get the reason for non-visit if exists
                non_visit_report = NonvisitReport.objects.filter(
                    customer_id=customer['customer_id'],
                    supply_date=request_date
                ).last()

                reason_for_non_visit = non_visit_report.reason if non_visit_report else None

                customer['last_sold_date'] = last_sold_date
                customer['reason_for_non_visit'] = reason_for_non_visit
                missed_customers.append(customer)

        log_activity(
                    created_by=request.user.username,
                    description=f"Missed Page for route ID: {route_id} on date: {date}."
                    )                   
        
        context = {
            'missed_customers': missed_customers,
            'route_id': route_id
        }

        return render(request, self.template_name, context)


class MissedOnDeliveryPrintView(View):
    
    template_name = 'accounts/missed_on_delivery_print.html'

    
    def get(self, request, route_id, *args, **kwargs):
        date = timezone.now().date()
        route = get_object_or_404(RouteMaster, route_id=route_id)

        planned_customers = find_customers(request, str(date), route_id)

        supplied_customers_ids = CustomerSupply.objects.filter(
            customer__routes__route_id=route_id,
            created_date__date=date
        ).values_list('customer_id', flat=True)

        missed_customers = []
        for customer in planned_customers:
            if customer['customer_id'] not in supplied_customers_ids:
                last_supply = CustomerSupply.objects.filter(
                    customer_id=customer['customer_id']
                ).order_by('-created_date').last()

                last_sold_date = last_supply.created_date if last_supply else None

                # Get the reason for non-visit if exists
                non_visit_report = NonvisitReport.objects.filter(
                    customer_id=customer['customer_id'],
                    supply_date=date
                ).last()

                reason_for_non_visit = non_visit_report.reason if non_visit_report else None

                customer['last_sold_date'] = last_sold_date
                customer['reason_for_non_visit'] = reason_for_non_visit
                missed_customers.append(customer)

            log_activity(
                    created_by=request.user.username,
                    description=f"Missed customers print successfully "
                )
            
        context = {
            'missed_customers': missed_customers,
            'route_id':route_id,
        }

        return render(request, self.template_name, context)

def processing_log_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Use today's date as the default if no date is provided
    if not start_date:
        start_date = date.today()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = date.today()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    logs = Processing_Log.objects.filter(created_date__date__range=(start_date, end_date)).order_by("-created_date")
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'accounts/processing_log_list.html', context)


class Gps_Route_List(View):
    template_name = 'accounts/gps_route_list.html'

    def get(self, request, *args, **kwargs):
        route_li = RouteMaster.objects.filter()
        context = {'route_li': route_li}
        return render(request, self.template_name, context)
    

def activate_gps_for_route(request, route_id):
    route = get_object_or_404(RouteMaster, route_id=route_id)
    
    gps_active = Customers.objects.filter(is_guest=False, routes=route, gps_module_active=True).exists()
    
    if gps_active:
        Customers.objects.filter(is_guest=False, routes=route).update(gps_module_active=False)

        GpsLog.objects.filter(route=route, gps_enabled=True, turn_off_time__isnull=True).update(turn_off_time=now())

        GpsLog.objects.create(
            route=route,
            user=request.user,
            gps_enabled=False,
            turn_on_time=now(),  
            turn_off_time=now() 
        )

        messages.success(request, f"GPS Lock disabled for all customers in route: {route.route_name}")

    else:
        Customers.objects.filter(is_guest=False, routes=route).update(gps_module_active=True)

        GpsLog.objects.create(
            route=route,
            user=request.user,
            gps_enabled=True,
            turn_on_time=now(),
            turn_off_time=None 
        )

        messages.success(request, f"GPS Lock enabled for all customers in route: {route.route_name}")

    return redirect('gps_settings')

def gps_lock_view(request, route_id):
    route = get_object_or_404(RouteMaster, route_id=route_id)
    gps_logs = GpsLog.objects.filter(route=route).order_by("-turn_on_time") 

    context = {
        "route": route,
        "gps_logs": gps_logs
    }
    return render(request, "accounts/gps_log_view.html", context)