import datetime

from django.db.models import Q, Sum
from django.core.management.base import BaseCommand

from customer_care.models import DiffBottlesModel
from master.models import RouteMaster
from client_management.models import DialyCustomers, Vacation
from accounts.models import CustomUser, Customers

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        route_instances = RouteMaster.objects.all()
        
        for route in route_instances:
            date = datetime.datetime.today().date()
            day_of_week = date.strftime('%A')
            week_num = (date.day - 1) // 7 + 1
            week_number = f'Week{week_num}'
            
            todays_customers = []
            
            vocation_customer_ids = Vacation.objects.filter(start_date__gte=date,end_date__lte=date).values_list('customer__pk')
            
            customers = Customers.objects.filter(is_guest=False, routes=route, is_calling_customer=False).exclude(pk__in=vocation_customer_ids)
            for customer in customers:
                if customer.visit_schedule:
                    for day, weeks in customer.visit_schedule.items():
                        if str(day_of_week) == str(day) and str(week_number) in weeks:
                            todays_customers.append(customer)

            for today_customer in todays_customers:
                today_customer,create = DialyCustomers.objects.get_or_create(
                    date=date,
                    customer=today_customer,
                    route=route,
                    qty=today_customer.no_of_bottles_required,
                    is_emergency=DiffBottlesModel.objects.filter(customer=today_customer,delivery_date=date).exists()
                )
                if (emergency_instances:=DiffBottlesModel.objects.filter(customer__pk=today_customer.pk,delivery_date=date)).exists():
                    required_qty = emergency_instances.aggregate(total_required=Sum('quantity_required'))['total_required'] or 0
                    today_customer.qty += required_qty
                    today_customer.save()
            
            # print(todays_customers)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all customers'))
