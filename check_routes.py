import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append('/Users/muhammedanshid/Desktop/mobiz_projects/SanaTest')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

from master.models import RouteMaster
from client_management.views import customer_outstanding_list

print(f"Routes in DB: {RouteMaster.objects.count()}")
for r in RouteMaster.objects.all():
    print(f" - {r.route_name} ({r.route_id})")
