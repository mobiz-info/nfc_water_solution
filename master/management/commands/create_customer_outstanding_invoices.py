import datetime
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser, Customers
from client_management.models import CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, OutstandingAmount
from invoice_management.models import Invoice, InvoiceItems
from master.models import RouteMaster
from product.models import ProdutItemMaster
from sales_management.models import CollectionItems, CollectionPayment

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        route = RouteMaster.objects.get(route_name="S-12B")
        date = datetime.datetime.strptime("2024-11-30", '%Y-%m-%d').date()
        
        # customers = Customers.objects.filter(is_guest=False, routes=route)
        
        # for customer in customers:
        #     outstanding_in = CustomerOutstanding.objects.filter(created_date__date=customer,product_type='amount')
        #     for i in outstanding_in:
        #         Invoice.objects.filter(invoice_no=i.invoice_no).delete()
        #     outstanding_in.delete()
        #     CustomerOutstandingReport.objects.filter(customer=customer,product_type='amount').delete()
            
        #     collections = CollectionPayment.objects.filter(customer=customer)
            
        #     for collection in collections:
        #         collection_items = CollectionItems.objects.filter(collection_payment=collection)
        #         for collection_item in collection_items:
        #             Invoice.objects.filter(invoice_no=collection_item.invoice).delete()
                    
        #     collections.delete()
                    
        
        oustandings = CustomerOutstanding.objects.filter(created_date__date=date, customer__routes=route)
        oustandings_invoice_nos = oustandings.values_list("invoice_no")
        supply_invoice_nos = CustomerSupply.objects.filter(customer__routes=route, created_date__date=date).values_list("invoice_no")
        
        # invoices = Invoice.objects.filter(created_date__date=date, customer__routes=route)
        
        # invoices = invoices.exclude(invoice_no__in=oustandings_invoice_nos).exclude(invoice_no__in=supply_invoice_nos)
        # invoices.delete()
        
        # for item in invoices:
        #     amout_total = item.amout_total
            
        #     item.amout_recieved = amout_total
        #     item.invoice_status = "paid"
        #     item.save()
            
        #     self.stdout.write(self.style.SUCCESS(f'Successfully updated {item.invoice_no}'))
         
        
        
        
        # for i in oustandings:
        #     Invoice.objects.filter(invoice_no=i.invoice_no).delete()
        
        # oustandings.delete()
        # CustomerOutstandingReport.objects.filter(customer__routes=route).delete()
        # user = CustomUser.objects.get(customer="S-41")
        
        
        
        
        for outstanding in oustandings:
            out_amounts = OutstandingAmount.objects.filter(customer_outstanding=outstanding)
            for out_amount in out_amounts:
            
                date_part = timezone.now().strftime('%Y%m%d')
                if CollectionPayment.objects.filter(customer=outstanding.customer, created_date__date__gt=outstanding.created_date.date()).exists():
                    amout_recieved = out_amount.amount
                else:
                    amout_recieved = 0
                
                # Create the invoice
                invoice = Invoice.objects.create(
                    created_date=out_amount.customer_outstanding.created_date,
                    net_taxable=out_amount.amount,
                    vat=0,
                    discount=0,
                    amout_total=out_amount.amount,
                    amout_recieved=amout_recieved,
                    customer=out_amount.customer_outstanding.customer,
                    reference_no=f"custom_id{out_amount.customer_outstanding.customer.custom_id}"
                )
                outstanding.invoice_no = invoice.invoice_no
                outstanding.save()
                
                if out_amount.customer_outstanding.customer.sales_type == "CREDIT":
                    invoice.invoice_type = "credit_invoice"
                    invoice.save()

                # Create invoice items
                item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                InvoiceItems.objects.create(
                    category=item.category,
                    product_items=item,
                    qty=0,
                    rate=out_amount.customer_outstanding.customer.rate,
                    invoice=invoice,
                    remarks='invoice genereted from backend reference no : ' + invoice.reference_no
                )
                
            oustandings.update(invoice_no=invoice.invoice_no)

        self.stdout.write(self.style.SUCCESS('Successfully updated visit schedule for customers with visit_schedule="Saturday"'))