from django.urls import path
from . import views

app_name = "custody"

urlpatterns = [
    path("custody_product_summary/", views.custody_product_summary, name="custody_product_summary"),
    path("customer_wise_custody_summary/", views.customer_wise_custody_summary, name="customer_wise_custody_summary"),
    path("custody/routes/<uuid:product_id>/",views.custody_route_summary,name="custody_route_summary"),
    path(
    "custody/customers/<uuid:product_id>/<uuid:route_id>/",
    views.custody_customer_summary,
    name="custody_customer_summary"
    ),
    path(
    "custody/ledger/<uuid:product_id>/<uuid:route_id>/<uuid:customer_id>/",
    views.custody_ledger,
    name="custody_ledger"
)
]
