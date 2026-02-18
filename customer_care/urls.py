from django.urls import path
from . views import *

urlpatterns = [
path('requesttype_list', RequestType_List.as_view(), name='requesttype_list'),
path('requesttype_create',RequestType_Create.as_view(), name='requesttype_create'),
path('requesttype_edit/<str:pk>', RequestType_Edit.as_view(), name='requesttype_edit'),
path('requesttype_details/<str:pk>', RequestType_Details.as_view(), name='requesttype_details'),
path('requesttype_delete/<uuid:pk>/', RequestType_Delete.as_view(), name='requesttype_delete'),


path('bottle_list/<str:pk>', Bottle_List.as_view(), name='bottle_list'),
path('diffbottles_create/<str:pk>', Diffbottles_Create.as_view(), name='diffbottles_create'),

path('coupon_purchase_list/<str:pk>', Coupon_Purchse_List.as_view(), name='coupon_purchase_list'),
path('coupon_purchase_create/<str:pk>', Coupon_Purchse_Create.as_view(), name='coupon_purchase_create'),

path('other_list/<str:pk>', Other_List.as_view(), name='other_list'),
path('otherreq_create/<str:pk>', Other_Req_Create.as_view(), name='otherreq_create'),

path('custody_pullout_list/<str:pk>', Custody_Pullout_List.as_view(), name='custody_pullout_list'),
path('custody_pullout_create/<str:pk>', Custody_Pullout_Create.as_view(), name='custody_pullout_create'),
path('get_item_quantity',get_item_quantity, name='get_item_quantity'),

# path('requestType',requestType, name='requestType'),
path('requestType', requestType.as_view(), name='requestType'),

path('custody_pullout/<str:pk>',custody_pullout, name='custody_pullout'),
path('change_of_address/<str:pk>',change_of_address, name='change_of_address'),
path('default_bottle_qty/<str:pk>',default_bottle_qty, name='default_bottle_qty'),

#create customer
path('createcustomer',createcustomer, name='createcustomer'),
path('new_request_home/<str:customer_id>', NewRequestHome.as_view(), name='new_request_home'),
path('water_delivery_status', WaterDeliveryStatus.as_view(), name='water_delivery_status'),
path('edit_quantity/<uuid:diffbottles_id>/', EditQuantityView.as_view(), name='edit_quantity'),
path('cancel_request/<uuid:diffbottles_id>/', CancelRequestView.as_view(), name='cancel_request'),
# path('reassign_request/<uuid:diffbottles_id>/', ReassignRequestView.as_view(), name='reassign_request'),
# path('next_delivery_date', find_next_delivery_date, name = 'nexr_delivery_date'),
path('reassign_request/<uuid:diffbottles_id>/',ReassignRequestView.as_view(), name='reassign_request'),

path('new_customer_request', new_customer_request.as_view(), name='new_customer_request'),
path('new-registered-customers', new_registered_customers, name='new_registered_customers'),

path('customer_request_type_list', CustomerRequestType_List.as_view(), name='customer_request_type_list'),
path('customer_requesttype_create',CustomerRequestType_Create.as_view(), name='customer_requesttype_create'),
path('customer_requesttype_edit/<str:pk>', CustomerRequestType_Edit.as_view(), name='customer_requesttype_edit'),
path('customer_requesttype_delete/<uuid:pk>/', CustomerRequestType_Delete.as_view(), name='customer_requesttype_delete'),

path("guest-customers/", GuestCustomerList.as_view(), name="guest_customers"),
path("assign-to-customer/<str:pk>/", EditGuestCustomerView.as_view(), name="assign_to_customer"),
path('guest-customer-orders/<uuid:customer_id>/', GuestCustomerOrders.as_view(), name='guest_customer_orders'),
path('approve-guest-order/<uuid:order_id>/', ApproveGuestOrder.as_view(), name='approve_guest_order'),

]