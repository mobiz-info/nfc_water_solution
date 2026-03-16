from django.urls import path
from . import views

app_name = "bottle_management"

urlpatterns = [
path("bottle-generator/", views.bottle_generator_page,name="bottle-generator"),
path("preview_bottles/", views.preview_bottles,name="preview_bottles"),
path(
    "save-bottles/",
    views.save_bottles,
    name="save_bottles"
),

path("nfc-mapping/", views.nfc_mapping_page, name="nfc_mapping"),
path("nfc-mapping/save/", views.nfc_mapping_save, name="nfc_mapping_save"),
path("get-available-bottles/", views.get_available_bottles, name="get_available_bottles"),
path("report/", views.bottle_stock_report, name="bottle_stock_report"),
path("movement-report/", views.periodic_bottle_movement_report, name="movement_report"),
path("bottle-cycle-report/", views.bottle_cycle_report, name="bottle_cycle_report"),
path("bottles/", views.bottles_report, name="bottles_report"),
path('bottle-delete/<int:pk>/', views.bottle_delete, name='bottle_delete'),
]