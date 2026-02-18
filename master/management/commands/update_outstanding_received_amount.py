import datetime
from decimal import Decimal
import random

from django.utils import timezone
from django.db.models import Q,Sum,DecimalField
from django.core.management.base import BaseCommand

from accounts.models import Customers
from invoice_management.models import Invoice, InvoiceItems
from product.models import ProdutItemMaster
from sales_management.models import CollectionPayment


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        route_name = "S-01"
        customer_pk = "a869440c-2dab-4d3b-bab8-d553d95b8c48"
        customer_instances = Customers.objects.filter(is_guest=False, pk=customer_pk)
        date_part = timezone.now().strftime('%Y%m%d')
        
        for customer in customer_instances:
            invo_ids = ""
            invoice_instances = Invoice.objects.filter(customer=customer,is_deleted=False).order_by("created_date")
            # if invo_ids:
            #     invoice_instances = invoice_instances.filter(invoice_no__in=invo_ids)
                
                # 1st step update all invoice received rate as 0
            invoice_instances.update(amout_recieved=0,invoice_status = "non_paid")
            
            # total_collection_amount = CollectionPayment.objects.filter(customer=customer).aggregate(total=Sum('amount_received', output_field=DecimalField()))['total'] or 0
            # remaining_amount = total_collection_amount
            
            balance_amount = Decimal(40)
            for invoice in invoice_instances:
                if invoice.amout_total < 0:
                    balance_amount += abs(invoice.amout_total) 
                
                if balance_amount >= 0:
                    total_amount = invoice.amout_total
                    
                    if balance_amount >= invoice.amout_total:
                        invoice.amout_recieved = total_amount
                    elif balance_amount < invoice.amout_total:
                        invoice.amout_recieved = balance_amount
                    if invoice.amout_total == invoice.amout_recieved:
                        invoice.invoice_status = "paid"
                    invoice.save()
                
                balance_amount -= Decimal(invoice.amout_total)
                
            #     invoice_amount = invoice.amout_total - invoice.amout_recieved
            #     if invoice_amount < 0:
            #         remaining_amount = remaining_amount + abs(invoice_amount)
            
            #         # Calculate the amount due for this invoice
            #         due_amount = invoice.amout_total - invoice.amout_recieved
            #         payment_amount = due_amount
                    
            #         # If remaining_amount is greater than zero and there is still due amount for the current invoice
            #         if remaining_amount != Decimal('0') and due_amount != Decimal('0'):
            #             # Calculate the payment amount for this invoice
            #             if due_amount < 0 or due_amount == remaining_amount:
            #                 payment_amount = due_amount
            #             elif due_amount > remaining_amount:
            #                 payment_amount = remaining_amount
            #             elif due_amount < remaining_amount:
            #                 payment_amount = due_amount
                        
            #             # Update the invoice balance and amount received
            #             invoice.amout_recieved += payment_amount
            #             invoice.save()
                        
            # if remaining_amount != Decimal('0'):
            #     negatieve_remaining_amount = -remaining_amount
                
            #     try:
            #         invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
            #         last_invoice_number = invoice_last_no.invoice_no

            #         # Validate the format of the last invoice number
            #         parts = last_invoice_number.split('-')
            #         if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
            #             prefix, old_date_part, number_part = parts
            #             new_number_part = int(number_part) + 1
            #             invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
            #         else:
            #             # If the last invoice number is not in the expected format, generate a new one
            #             random_part = str(random.randint(1000, 9999))
            #             invoice_number = f'WTR-{date_part}-{random_part}'
            #     except Invoice.DoesNotExist:
            #         random_part = str(random.randint(1000, 9999))
            #         invoice_number = f'WTR-{date_part}-{random_part}'
                
            #     # Create the invoice for the refund amount
            #     invoice = Invoice.objects.create(
            #         invoice_no=invoice_number,
            #         created_date=datetime.datetime.today(),
            #         net_taxable=negatieve_remaining_amount,
            #         vat=0,
            #         discount=0,
            #         amout_total=negatieve_remaining_amount,
            #         amout_recieved=0,
            #         customer=customer,
            #         reference_no=f"custom_id{customer.custom_id}"
            #     )
            #     # customer_outstanding.invoice_no = invoice.invoice_no
            #     # customer_outstanding.save()
                
            #     if customer.sales_type == "CREDIT":
            #         invoice.invoice_type = "credit_invoice"
            #         invoice.save()

            #     # Create invoice items
            #     item = ProdutItemMaster.objects.get(product_name="5 Gallon")
            #     InvoiceItems.objects.create(
            #         category=item.category,
            #         product_items=item,
            #         qty=0,
            #         rate=customer.rate,
            #         invoice=invoice,
            #         remarks='invoice generated from collection: ' + invoice.reference_no
            #     )
                
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {invoice.invoice_no}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all customers'))
