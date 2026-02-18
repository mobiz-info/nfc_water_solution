import datetime
import random

from django.db.models import Q
from django.core.management.base import BaseCommand

from decimal import Decimal

from accounts.models import CustomUser
from client_management.models import CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyItems, DialyCustomers, InactiveCustomers, OutstandingAmount
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from master.models import RouteMaster
from sales_management.models import Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        for route in RouteMaster.objects.all():
            route_name = route.route_name
            
            start_date = datetime.date(2025, 9, 1)
            end_date = datetime.date.today() 
            
            dates = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

            for date in dates:
            
                supply_date = date
                
                # outstanding_customer_ids = CustomerOutstanding.objects.filter(customer__routes__route_name=route_name,created_date__date=supply_date, product_type="amount").values_list("customer__pk")
                supplies = CustomerSupply.objects.filter(customer__routes__route_name=route_name, created_date__date=supply_date)
                # .exclude(customer__pk__in=outstanding_customer_ids)
                
                # print(len(supplies.values_list("customer__custom_id")))
                
                for supply in supplies:
                    
                    if supply.customer.sales_type == "CASH" or supply.customer.sales_type == "CREDIT" :
                        if (supply.amount_recieved != supply.subtotal) and not CustomerOutstanding.objects.filter(customer=supply.customer, invoice_no=supply.invoice_no, created_date__date=supply_date).exists():
                            if supply.amount_recieved < supply.subtotal:
                                balance_amount = supply.subtotal - supply.amount_recieved
                                
                                customer_outstanding_amount = CustomerOutstanding.objects.create(
                                    product_type="amount",
                                    created_by=supply.created_by,
                                    customer=supply.customer,
                                    created_date=supply.created_date,
                                    invoice_no = supply.invoice_no
                                )

                                outstanding_amount = OutstandingAmount.objects.create(
                                    amount=balance_amount,
                                    customer_outstanding=customer_outstanding_amount,
                                )
                                outstanding_instance = {}

                                try:
                                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=supply.customer,product_type="amount")
                                    outstanding_instance.value += Decimal(outstanding_amount.amount)
                                    outstanding_instance.save()
                                except:
                                    outstanding_instance = CustomerOutstandingReport.objects.create(
                                        product_type='amount',
                                        value=outstanding_amount.amount,
                                        customer=outstanding_amount.customer_outstanding.customer
                                    )
                                    
                            elif supply.amount_recieved > supply.subtotal:
                                balance_amount = supply.amount_recieved - supply.subtotal
                                
                                customer_outstanding_amount = CustomerOutstanding.objects.create(
                                    product_type="amount",
                                    created_by=supply.created_by,
                                    customer=supply.customer,
                                    created_date=supply.created_date,
                                    invoice_no = supply.invoice_no
                                )

                                outstanding_amount = OutstandingAmount.objects.create(
                                    amount=balance_amount,
                                    customer_outstanding=customer_outstanding_amount,
                                )
                                
                                outstanding_instance=CustomerOutstandingReport.objects.get(customer=supply.customer,product_type="amount")
                                outstanding_instance.value -= Decimal(balance_amount)
                                outstanding_instance.save()
                            
                
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated {supply.invoice_no}'))
                    
                self.stdout.write(self.style.SUCCESS(f'Successfully updated date {supply_date}'))
                
            self.stdout.write(self.style.WARNING(f'Successfully updated route {route_name}'))
                
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))


# S-12B, S-02, S-13, S-16,S-19, S-21, S-38, S-40, S-41, S-42, S-45