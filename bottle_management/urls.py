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
]