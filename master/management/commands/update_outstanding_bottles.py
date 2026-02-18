import datetime

from django.core.management.base import BaseCommand

from client_management.models import CustomerSupply, CustomerOutstanding, OutstandingProduct, CustomerOutstandingReport

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        date = datetime.datetime.strptime("2024-10-02", '%Y-%m-%d').date()
        route_name = "test_route"
        customer_id = ""
        
        suply_intances = CustomerSupply.objects.filter(customer__routes__route_name=route_name)
        
        if customer_id:
            suply_intances = suply_intances.filter(customer__pk=customer_id)
            
        CustomerOutstanding.objects.filter(customer__routes__route_name=route_name,product_type="emptycan").delete()
        CustomerOutstandingReport.objects.filter(customer__routes__route_name=route_name,product_type="emptycan").delete()
        
        for supply in suply_intances:
            total_supply_qty = supply.get_total_supply_qty() + supply.allocate_bottle_to_free - supply.allocate_bottle_to_pending - supply.allocate_bottle_to_custody
            total_collected_bottles = supply.collected_empty_bottle
            outstanding_bottles = total_supply_qty - total_collected_bottles
            
            # if total_supply_qty > total_collected_bottles:
            #     outstanding_bottles = total_supply_qty - total_collected_bottles
            # else:
            #     outstanding_bottles = total_collected_bottles - total_supply_qty
            
            if outstanding_bottles != 0 :
                outstanding_data = CustomerOutstanding.objects.create(
                    customer=supply.customer,
                    product_type="emptycan",
                    invoice_no=supply.invoice_no,
                    created_by=supply.created_by,
                    created_date=supply.created_date,
                )
                
                # if outstanding_bottles < 0:
                #     outstanding_bottles_value = abs(outstanding_bottles)
                # else:
                #     outstanding_bottles_value = outstanding_bottles
                
                OutstandingProduct.objects.create(
                    customer_outstanding=outstanding_data,
                    empty_bottle=outstanding_bottles,
                )
                
                out_report,create_report = CustomerOutstandingReport.objects.get_or_create(
                    customer=supply.customer,
                    product_type="emptycan"
                )
                
                out_report.value += outstanding_bottles
                out_report.save()
            
        
            self.stdout.write(self.style.WARNING(f'Successfully updated {supply.customer.custom_id}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all'))
