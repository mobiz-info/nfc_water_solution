from django.urls import path
from .views import *

urlpatterns = [
    # path('api/customerorder/', CustomerOrder.as_view(), name='customer_order_api'),
    path('order_change_reason', order_change_reason, name="order_change_reason"),
    path('reason_add',  Reason_Add.as_view(), name="reason_add"),
    path('reason_edit/<uuid:reason_id>',  Reason_Edit.as_view(), name="reason_edit"),
    path('reason_delete/<uuid:reason_id>',  Reason_Delete.as_view(), name="reason_delete"),

    path('filter_route/<str:action>', filter_route, name="filter_route"),

    # Change
    path('order_change',  order_change, name="order_change"),
    path('order_change_list/<uuid:route_id>/', order_change_list, name="order_change_list"),
    path('order_change_list_excel/<uuid:route_id>/', order_change_list_excel, name="order_change_list_excel"),
    path('order_change_add/<uuid:route_id>',  Order_change_Add.as_view(), name="order_change_add"),
    path('order_change_edit/<uuid:order_change_id>',  Order_change_Edit.as_view(), name="order_change_edit"),
    path('order_change_delete/<uuid:order_change_id>',  Order_change_Delete.as_view(), name="order_change_delete"),

    # Return
    path('order_return',  order_return, name="order_return"),
    path('order_return_list/<uuid:route_id>/', order_return_list, name="order_return_list"),
    path('order_return_list_excel/<uuid:route_id>/', order_return_list_excel, name="order_return_list_excel"),
    path('order_return_add/<uuid:route_id>',  Order_return_Add.as_view(), name="order_return_add"),
    path('order_return_edit/<uuid:order_return_id>',  Order_return_Edit.as_view(), name="order_return_edit"),
    path('order_return_delete/<uuid:order_return_id>',  Order_Return_Delete.as_view(), name="order_return_delete"),


    path('order_create/', OrderCreate.as_view(), name='order-create'),
    path('order_update/<uuid:pk>/', OrderUpdate.as_view(), name='order_update'),
    path('order_delete/<uuid:pk>/', OrderDelete.as_view(), name='order_delete'),
    path('order_list', order_list, name='order_list'),
    
    path('order_by_date', order_by_date, name="order_by_date"),
    path('order_by_route/<uuid:route_id>/<str:date>/<int:salesman_id>', order_by_route, name="order_by_route"),
    path('order_excel/<uuid:route_id>/<str:date>', order_excel, name="order_excel"),
    
]
