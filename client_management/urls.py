from django.urls import path
from .views import *
from django.urls import reverse

from django.urls import path,re_path
from . views import *

urlpatterns = [
        path('customer_custody_item/<str:customer_id>', customer_custody_item, name='customer_custody_item'),
        path('get_custody_items', get_custody_items, name='get_custody_items'),

        #vacation
        path('vacation_list', vacation_list, name="vacation_list"),
        path('vacation_add', Vacation_Add.as_view(), name="vacation_add"),
        path('vacation_edit/<uuid:vacation_id>', Vacation_Edit.as_view(), name='vacation_edit'),
        path('vacation_delete/<uuid:vacation_id>',  Vacation_Delete.as_view(), name="vacation_delete"),
        path('vacation_route',  RouteSelection.as_view(), name="vacation_route"),

        # path('vacation_list', vacation_list, name="vacation_list"),
        path('vacation/', vacation_route_summary, name='vacation_route_summary'),
        path('vacation/route/<uuid:route_id>/',vacation_list_by_route,name='vacation_list_by_route'),


        # path('create_custody_item/<uuid:pk>', CreateCustodyItemView.as_view(), name='create_custody_item'),
        path('customer_custody_list', CustomerCustodyList.as_view(), name='customer_custody_list'),
        path('add_custody_items', AddCustodyItems.as_view(), name='add_custody_items'),
        path('add_custody_list',AddCustodyList.as_view(),name='add_custody_list'),
        path('edit_custody_item',EditCustodyItem.as_view(),name='add_custody_list'),
        # path('edit_custody_item',DeleteCustodyItem.as_view(),name='add_custody_list'),
        # path('pullout_list<str:pk>', PulloutListView.as_view(), name='pullout_list'),

        # path('count_coupen', CountCoupen, name="count_coupen"),
        
        re_path(r'customer-supply-list/$', customer_supply_list, name='customer_supply_list'),
        re_path(r'change_supply_date/$', change_supply_date, name='change_supply_date'),
        path('view_invoice/<path:invoice_no>/', view_invoice, name='view_invoice'),
        re_path(r'supply-customers/$', customer_supply_customers, name='customer_supply_customers'),
        re_path(r'create-customer-suppply/(?P<pk>.*)/$', create_customer_supply, name='create_customer_supply'),
        re_path(r'^info-customer-suppply/(?P<pk>.*)/$', customer_supply_info, name='customer_supply_info'),
        re_path(r'^edit-customer-suppply/(?P<pk>.*)/$', edit_customer_supply, name='edit_customer_supply'),
        re_path(r'^delete-customer-suppply/(?P<pk>.*)/$', delete_customer_supply, name='delete_customer_supply'),

#------------------------------Report-------------------------

        path('client_report', client_report, name='client_report'),
        path('clientdownload_pdf/<uuid:customer_id>/', clientdownload_pdf, name='clientdownload_pdf'),
        path('clientexport_to_csv/<uuid:customer_id>/', clientexport_to_csv, name='clientexport_to_csv'),
        path('custody_items_list_report', custody_items_list_report, name='custody_items_list_report'),
        path('custody_issue', custody_issue, name='custody_issue'),
        path('customer_custody_items/<uuid:customer_id>/', get_customercustody, name='customer_custody_items'),
        path('custody_report', custody_report, name='custody_report'),
   
        path('coupon_count/<uuid:pk>/', CouponCountList.as_view(), name='coupon_count_list'),

        # path('edit-coupon-count/<uuid:pk>/', edit_coupon_count, name='edit_coupon_count'),
        path('new-coupon-count/<uuid:pk>/', new_coupon_count, name='new_coupon_count'),
        path('delete-coupon-count/<uuid:pk>/', delete_count, name='delete_count'),
        
        #customer outstanding
        re_path(r'^customer-outstanding/$', customer_outstanding_list, name='customer_outstanding_list'),
        path('print_customer_outstanding/', print_customer_outstanding, name='print_customer_outstanding'),
        path('excel_customer_outstanding/', export_customer_outstanding_to_excel, name='excel_customer_outstanding'),
        re_path(r'^edit_customer_outstanding/(?P<outstanding_pk>.*)/$', edit_customer_outstanding, name='edit_customer_outstanding'),
        re_path(r'outstanding_list/$', outstanding_list, name='outstanding_list'),
        path('print-outstanding-report/', print_outstanding_report, name='print_outstanding_report'),
        re_path(r'^create-customer-outstanding/$', create_customer_outstanding, name='create_customer_outstanding'),
        re_path(r'^customer-outstanding-details/(?P<customer_pk>.*)/$', customer_outstanding_details, name='customer_outstanding_details'),
        re_path(r'^customer-outstanding-view-print/(?P<customer_pk>.*)/$', customer_outstanding_print, name='customer_outstanding_print'),
        re_path(r'^customer-outstanding-view/(?P<customer_pk>.*)/$', customer_outstanding_view, name='customer_outstanding_view'),

        re_path(r'^delete-customer-outstanding/(?P<pk>.*)/$', delete_outstanding, name='delete_outstanding'),
        path("delete_outstanding_adjustment/<uuid:pk>/",delete_outstanding_adjustment,name="delete_outstanding_adjustment" ),

        # Customer count
        path('customer_count', customer_count, name="customer_count"),

        path('bottle_count', bottle_count, name="bottle_count"),
        path('bottle-count-route-wise/<uuid:route_id>', bottle_count_route_wise, name='bottle_count_route_wise'),

        path('customer-orders-list', customer_orders, name="customer_orders_list"),
        path('customer-orders-status-acknowledge/<uuid:pk>', customer_order_status_acknowledge, name="customer_order_status_acknowledge"),
        
        path('nonvisitreason_List', nonvisitreason_List, name="nonvisitreason_List"),
        path('create_nonvisitreason', create_nonvisitreason, name="create_nonvisitreason"),
        path('delete_nonvisitreason/<uuid:id>/', delete_nonvisitreason, name='delete_nonvisitreason'),

        path('upload-outstanding/', upload_outstanding, name='upload_outstanding'),

        path('ageing_report/', ageing_report_view, name='ageing_report'),
        path('ageing_report_print/', print_ageing_report_view, name='print_ageing_report'),
        path('ageing_report_excel/',ageing_report_excel, name='ageing_report_excel'),
        path('customer-outstanding-detail/<uuid:customer_id>/', customer_outstanding_detail, name='customer_outstanding_detail'),
        path('export_customer_outstanding/<uuid:customer_id>/', export_customer_outstanding_to_excel, name='export_customer_outstanding'),
        path('print_customer_outstandings/<uuid:customer_id>/', print_customer_outstandings, name='print_customer_outstandings'),
        
        
        re_path(r'^customer_transaction_list/$', customer_transaction_list, name='customer_transaction_list'),
        re_path(r'^customer_transaction_print/$', customer_transaction_print, name='customer_transaction_print'),
        
        re_path(r'^eligible-customer-conditions/$', eligible_customers_conditions, name='eligible_customers_conditions'),
        re_path(r'^create-eligible-customer-conditions/$', create_eligible_customers_condition, name='create_eligible_customers_condition'),
        re_path(r'^edit-eligible-customer-conditions/(?P<pk>.*)/$', edit_eligible_customers_condition, name='edit_eligible_customers_condition'),
        re_path(r'^delete-eligible-customer-conditions/(?P<pk>.*)/$', delete_eligible_customers_condition, name='delete_eligible_customers_condition'),
        
        re_path(r'^eligible-customers/$', eligible_customers, name='eligible_customers'),
        
        
        #-----------------------------------------Audit---------------------------------------------
        path("select_executive/", MarketingExecutiveRoutesView.as_view(), name="select_executive"),
        path("audit_customer_list/<uuid:route_id>/", CustomerListView.as_view(), name="audit_customer_list"),
        path("audit_details/<uuid:customer_id>/", AuditDetailsView.as_view(), name="audit_details"),
        
        path("customer_custody_stock/", customer_custody_stock, name="customer_custody_stock"),
        path('custody-item-return-pull/<uuid:stock_id>/', custody_item_return_view, name='custody_item_return_pull'),

        path("customer-outstanding-report/", customer_outstanding_report, name="customer_outstanding_report"),
        
        re_path(r'^salesman_outstanding_list/$', salesman_outstanding_list, name='salesman_outstanding_list'),
        path("salesman/invoices/",salesman_invoice_list,name="salesman_invoice_list"),
]
