import json
import datetime
from datetime import timedelta, timezone
import random
import uuid

from django.utils import timezone

from accounts.models import Processing_Log, Staff_Day_of_Visit
from invoice_management.models import Invoice
from sales_management.models import Receipt


def generate_form_errors(args,formset=False):
    i = 1
    message = ""
    if not formset:
        for field in args:	
            if field.errors:
                message += "\n"
                message += field.label + " : "
                message += str(field.errors)

        for err in args.non_field_errors():
            message += str(err)
    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message += "\n"
                    message += field.label + " : "
                    message += str(field.errors)
            for err in form.non_field_errors():
                message += str(err)

    message = message.replace("<li>", "")
    message = message.replace("</li>", "")
    message = message.replace('<ul class="errorlist">', "")
    message = message.replace("</ul>", "")
    return message


def generate_serializer_errors(args):
    message = ""
    # print (args)
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]

def get_custom_id(model):
    custom_id = 1  # Default starting ID
    
    try:
        # Get the latest record based on created_date
        latest_custom_id = model.objects.all().order_by("-created_date").first()
        if latest_custom_id:
            custom_id = int(latest_custom_id.custom_id) + 1
        
        # Ensure the generated ID is unique
        while model.objects.filter(custom_id=custom_id).exists():
            custom_id += 1
    except Exception as e:
        # Handle any unexpected errors (e.g., missing fields, etc.)
        print(f"Error generating custom_id: {e}")
    
    return custom_id


def get_dates_for_days(days_of_week,week_number):
    # Get today's date
    today = datetime.datetime.today()
    # Get the current weekday (0 = Monday, 6 = Sunday)
    current_weekday = week_number
    # print("curent week day",current_weekday)

    # Function to get the date for a specific weekday in the current week
    def get_date_for_weekday(target_weekday):
        days_difference = target_weekday - current_weekday
        target_date = today + datetime.timedelta(days=days_difference)
        return target_date

    # Get the dates for the specified days
    days_of_week_indices = {day: i for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}
    visit_dates = {day: get_date_for_weekday(days_of_week_indices[day]).strftime('%Y-%m-%d') for day in days_of_week}

    return visit_dates

def get_dates_for_days(days_of_week, week_offset=0):
    # Get today's date
    today = datetime.datetime.today()
    # Get the current weekday (0 = Monday, 6 = Sunday)
    current_weekday = today.weekday()
    
    # Adjust for the week offset
    today += datetime.timedelta(days=week_offset * 7)

    # Function to get the date for a specific weekday in the current week
    def get_date_for_weekday(target_weekday):
        days_difference = target_weekday - current_weekday
        target_date = today + datetime.timedelta(days=days_difference)
        return target_date

    # Get the dates for the specified days
    days_of_week_indices = {day: i for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}
    visit_dates = {day: get_date_for_weekday(days_of_week_indices[day]).strftime('%Y-%m-%d') for day in days_of_week}

    return visit_dates

def get_next_visit_date(visit_schedule):
    def find_next_visit(week_offset):
        date = datetime.datetime.today() + datetime.timedelta(days=week_offset * 7)
        week_num = (date.day - 1) // 7 + 1
        week_number = f'Week{week_num}'
        
        week_days = []
        

        for day, weeks in visit_schedule.items():
            if week_number in weeks:
                week_days.append(day)
        
        visit_dates = get_dates_for_days(week_days, week_offset)
        
        # Convert string dates back to datetime objects
        date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in visit_dates.values()]
        
        # Filter out dates that are not greater than today
        future_dates = [date for date in date_objects if date > datetime.datetime.today()]
        
        # Find the minimum date that is greater than today
        if future_dates:
            min_date = min(future_dates)
            return min_date.strftime('%d-%m-%Y')
        else:
            return None

    # Check the current week
    next_visit = find_next_visit(0)
    if next_visit:
        return next_visit
    
    # If no visits in the current week, check the next week
    next_visit = find_next_visit(1)
    if next_visit:
        return next_visit
    
    return "-"


def log_activity(created_by, description, created_date=None):
    
    if created_date is None:
        created_date = timezone.now()

    Processing_Log.objects.create(
        created_by=created_by,
        description=description,
        created_date=created_date
    )


# # Example usage
# visit_schedule = '{"Friday": ["Week2", "Week4", "Week1", "Week5"], "Monday": ["Week1", "Week5", "Week4", "Week2", "Week3"], "Sunday": ["Week4", "Week1"], "Tuesday": ["Week5", "Week4"], "Saturday": ["Week4", "Week5", "Week2"], "Thursday": ["Week5", "Week1"], "Wednesday": ["Week2", "Week3", "Week4"]}'
# next_visit_dates = get_next_visit_date(visit_schedule)
# print(next_visit_dates)

def generate_invoice_no(date):
    if (invoices:=Invoice.objects.filter(created_date__date=date,is_deleted=False)).exists():
        last_invoice = invoices.latest('created_date')
        last_invoice_number = last_invoice.invoice_no
        prefix, date_part, number_part = last_invoice_number.split('-')
        new_number_part = int(number_part) + 1
        invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
    else:
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = str(random.randint(1000, 9999))
        invoice_number = f'WTR-{date_part}-{random_part}'
        
    return invoice_number

def generate_receipt_no(date):
    return f"RCT-{date}-{uuid.uuid4().hex[:8].upper()}"
