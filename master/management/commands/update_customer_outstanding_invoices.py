import random
from datetime import datetime

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db.models import Sum, Value, DecimalField, Min

from accounts.models import CustomUser, Customers
from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice, InvoiceItems
from product.models import ProdutItemMaster

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        date = datetime.strptime("2025-08-02", '%Y-%m-%d')
        date_part = date.strftime('%Y%m%d')
        
        oustandings = CustomerOutstanding.objects.filter(created_date__date=date,customer__routes__route_name="S-12D")
        
        for oustanding in oustandings:
            # oustanding_amount = OutstandingAmount.objects.filter(customer_outstanding=oustanding).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            # invoice = Invoice.objects.filter(invoice_no=oustanding.invoice_no,customer=oustanding.customer,amout_total=oustanding_amount)
            if not Invoice.objects.filter(invoice_no=oustanding.invoice_no,is_deleted=False,customer=oustanding.customer).exists():
                
                # Create the invoice
                invoice = Invoice.objects.create(
                    created_date=oustanding.created_date,
                    net_taxable=oustanding.get_outstanding_count(),
                    vat=0,
                    discount=0,
                    amout_total=oustanding.get_outstanding_count(),
                    amout_recieved=0,
                    customer=oustanding.customer,
                    invoice_type = "credit_invoice",
                    reference_no=f"custom_id{oustanding.customer.custom_id}"
                )
                
                # Create invoice items
                item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                water_rate = oustanding.customer.get_water_rate()
                InvoiceItems.objects.create(
                    category=item.category,
                    product_items=item,
                    qty=0,
                    rate=water_rate,
                    invoice=invoice,
                    remarks='invoice genereted from backend reference no : ' + invoice.reference_no
                )
                
                if oustanding.invoice_no != "":
                    invoice.invoice_no = oustanding.invoice_no
                    invoice.save()
                    
                oustanding.invoice_no = invoice.invoice_no
                oustanding.save()
            
            
            #  duplicate_invoices = Invoice.objects.filter(
            #     created_date__date=date,
            #     customer__routes__route_name="S-12B"
            # ).values('invoice_no').annotate(
            #     id_count=Count('id')
            # ).filter(id_count__gt=1).values_list('invoice_no', flat=True)

            # # Fetch all duplicate invoices with 'amount_received = 0'
            # invoices_to_delete = Invoice.objects.filter(
            #     amout_recieved=0,
            #     invoice_no__in=duplicate_invoices
            # )

            # # Log duplicate invoices for debugging
            # print(f"Duplicate Invoices: {list(duplicate_invoices)}")
            
            # invoices_to_delete.delete()
            
            # # try:
            # date_part = date.strftime('%Y%m%d')
            # if (invoice_last_no:=Invoice.objects.filter(is_deleted=False)).exists():
            #     invoice_last_no = invoice_last_no.latest('created_date')
            #     last_invoice_number = invoice_last_no.invoice_no

            #     # Validate the format of the last invoice number
            #     parts = last_invoice_number.split('-')
            #     if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
            #         prefix, old_date_part, number_part = parts
            #         new_number_part = int(number_part) + 1
            #         invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
            #     else:
            #         # If the last invoice number is not in the expected format, generate a new one
            #         random_part = str(random.randint(1000, 9999))
            #         invoice_number = f'WTR-{date_part}-{random_part}'
            # else:
            #     random_part = str(random.randint(1000, 9999))
            #     invoice_number = f'WTR-{date_part}-{random_part}'
            
            # # Create the invoice
            # invoice = Invoice.objects.create(
            #     invoice_no=invoice_number,
            #     created_date=oustanding.created_date,
            #     net_taxable=oustanding_amount,
            #     vat=0,
            #     discount=0,
            #     amout_total=oustanding_amount,
            #     amout_recieved=0,
            #     customer=oustanding.customer,
            #     reference_no=f"ouststanding :{oustanding.customer.custom_id}"
            # )
            # oustanding.invoice_no = invoice.invoice_no
            # oustanding.save()
            
            # if oustanding.customer.sales_type == "CREDIT":
            #     invoice.invoice_type = "credit_invoice"
            #     invoice.save()

            # # Create invoice items
            # item = ProdutItemMaster.objects.get(product_name="5 Gallon")
            # water_rate = oustanding.customer.get_water_rate()
            # InvoiceItems.objects.create(
            #     category=item.category,
            #     product_items=item,
            #     qty=0,
            #     rate=water_rate,
            #     invoice=invoice,
            #     remarks='reference no : ' + invoice.reference_no
            # )

            self.stdout.write(self.style.SUCCESS(f'Successfully updated for customer ID {oustanding.customer.custom_id}'))
            # except Exception as e:
            #     self.stdout.write(self.style.ERROR(f'Error updating customer ID {oustanding.customer.customer_id}: {e}'))
