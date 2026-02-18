from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        customers = Customers.objects.all()
        
        for customer in customers:
            if customer.customer_name and len(customer.customer_name) >= 4 and customer.mobile_no and len(customer.mobile_no) >= 4:
                # Extract parts for username
                customer_name_part = customer.customer_name[:4].lower()
                mobile_no_part = customer.mobile_no[-4:]
                username = customer_name_part + mobile_no_part
                username = username.replace(" ", "-")  # Replace spaces with hyphens
                password = customer.mobile_no  # This will be hashed
                
                try:
                    if customer.user_id:
                        custom_user = CustomUser.objects.get(pk=customer.user_id.pk)
                        custom_user.username = username
                        custom_user.set_password(password)  # Properly hash the password
                        custom_user.save()
                    else:
                        # Create a new user
                        custom_user = CustomUser.objects.create(
                            username=username
                        )
                        custom_user.set_password(password)  # Properly hash the password
                        custom_user.save()
                        customer.user_id = custom_user
                        customer.save()

                    self.stdout.write(self.style.SUCCESS(f'Successfully updated username and password for customer ID {customer.customer_id}, {username}, {password}'))
                except CustomUser.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User associated with customer ID {customer.customer_id} does not exist'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating customer ID {customer.customer_id}: {e}'))
