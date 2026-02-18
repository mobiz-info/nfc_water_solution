from faker import Faker
import random

fake = Faker()

def generate_fake_location_data():
    CUSTOMER_TYPE_CHOICES = ["HOME", "CORPORATE", "SHOP"]
    SALES_TYPE_CHOICES = ["CASH COUPON", "CREDIT COUPON", "CASH", "CREDIT"]

    fake_data = {
        "customer_name": fake.name(),
        "building_name": fake.street_address(),  # Using street_address as a substitute for building_name
        "door_house_no": fake.building_number(),
        "floor_no": fake.random_number(digits=2),
        "sales_staff": random.randint(1, 10),  # Assuming CustomUser IDs are from 1 to 10
        "mobile_no": fake.phone_number(),
        "whats_app": fake.phone_number(),
        "email_id": fake.email(),
        "gps_latitude": fake.latitude(),
        "gps_longitude": fake.longitude(),
        "customer_type": random.choice(CUSTOMER_TYPE_CHOICES),
        "sales_type": random.choice(SALES_TYPE_CHOICES),
        "no_of_bottles_required": random.randint(1, 20),
        "max_credit_limit": random.randint(1000, 5000),
        "credit_days": random.randint(1, 30),
        "no_of_permitted_invoices": random.randint(1, 10),  # Assuming BranchMaster IDs are from 1 to 5
        "is_active": fake.boolean(),
        "visit_schedule":{
            'monday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'tuesday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'wednesday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'thursday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'friday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'saturday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
            'sunday': [fake.random_element(['week1', 'week2']), fake.random_element(['week3', 'week4'])],
        }
    }
    return fake_data

# Generate fake data
fake_location_data = generate_fake_location_data()
print(fake_location_data)