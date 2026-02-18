from django.urls import path,re_path
from .views import *



urlpatterns = [
    path('van',van, name='van'),
    path('create_van/',create_van, name='create_van'),
    path('view_van/<uuid:van_id>/', view_van, name="view_van"),
    path('edit_van/<uuid:van_id>/', edit_van, name="edit_van"),

    #--Need to remove Start ----
    path('delete_van/<uuid:van_id>/', delete_van, name='delete_van'),
    path('van_assign/', view_association, name='van_assign'),
    path('create_assign/', create_association, name='create_association'),
    path('edit_assign/<uuid:van_id>/', edit_assign, name='edit_assign'),
    path('delete_assign/<uuid:van_id>/', delete_assign, name='delete_assign'),
    # Need to remove End------
    
    path('route_assign/<str:van_id>', route_assign, name="route_assign"),
    path('delete_route_assign', delete_route_assign, name="delete_route_assign"),

    path('licence_list', Licence_List.as_view(), name="licence_list"),
    path('licence_add', Licence_Adding.as_view(), name="licence_add"),
    path('licence_edit/<str:pk>/', License_Edit.as_view(), name='licence_edit'),
    path('licence_delete/<str:plate>/', licence_delete, name='licence_delete'),

    path('schedule_view', schedule_view, name="schedule_view"),
    path('schedule_by_route/<str:def_date>/<uuid:route_id>/<str:trip>', schedule_by_route, name="schedule_by_route"),
    
    path('pdf_download/<uuid:route_id>/<str:def_date>/<str:trip>', pdf_download, name="pdf_download"),
    path('excel_download/<uuid:route_id>/<str:def_date>/<str:trip>', excel_download, name="excel_download"),

    # Expense
    path('expensehead_list', ExpenseHeadList.as_view(), name="expensehead_list"),
    path('expensehead_add', ExpenseHeadAdd.as_view(), name="expensehead_add"),
    path('expensehead_edit/<uuid:expensehead_id>', ExpenseHeadEdit.as_view(), name="expensehead_edit"),
    path('expensehead_delete/<uuid:expensehead_id>', ExpenseHeadDelete.as_view(), name="expensehead_delete"),


    path('expense_list', ExpenseList.as_view(), name="expense_list"),
    path('expense_add', ExpenseAdd.as_view(), name="expense_add"),
    path('expense_edit/<uuid:expense_id>', ExpenseEdit.as_view(), name="expense_edit"),
    path('expense_delete/<uuid:expense_id>', ExpenseDelete.as_view(), name="expense_delete"),
    
                                   
    # path('van-stock-product', VanStock.as_view(), name="vanstock"),
    # path('van-stock-product', VanStockList.as_view(), name="vanstock"),
    path('van-stock-product', VanProductStockList.as_view(), name="vanstock_product"),
    path('van-stock-product-update/<uuid:pk>/', VanProductStockUpdate.as_view(), name="vanstock_product_update"),
    
    path('offload', offload, name="offload"),
    path('get-van-coupon-bookno/', get_van_coupon_bookno, name="get_van_coupon_bookno"),
    path('view_item_details/<str:pk>/', View_Item_Details.as_view(), name="view_item_details"),
    path('edit-product-count/<uuid:pk>/', EditProductView.as_view(), name="edit_product_count"),
    path('edit-coupon-count/<uuid:van_pk>/', EditCouponView.as_view(), name="edit_coupon_count"),
    
    path('salesman-requests/',salesman_requests, name="salesman_requests"),

    path('bottle_allocation/',BottleAllocationn, name='bottle_allocation'),
    path('edit_bottle_allocation/<uuid:route_id>/',EditBottleAllocation, name='edit_bottle_allocation'),
    
    path('van_coupon_stock/', VanCouponStockList.as_view(), name='van_coupon_stock'),
    path('van_damage_stock/', VanDamageBottleList.as_view(), name='van_damage_stock'),
    path('van_damage_stock_report/', van_damage_stock_report, name='van_damage_stock_report'),
    path('van_damage_stock_print/', van_damage_stock_print, name='van_damage_stock_print'),
    path('van_damage_stock_excel/', van_damage_stock_excel, name='van_damage_stock_excel'),

    path('route-damage/<uuid:route_id>/', route_damage_detail, name='route_damage_detail'),
    path('route-damage-print/<uuid:route_id>/', route_damage_detail_print, name='route_damage_detail_print'),
    path('route-damage-excel/<uuid:route_id>/', route_damage_detail_excel, name='route_damage_detail_excel'),
    path('edit-van-sale-damage/<uuid:pk>/', edit_van_sale_damage, name='edit_van_sale_damage'),
    path('delete-van-sale-damage/<uuid:pk>/', delete_van_sale_damage, name='delete_van_sale_damage'),

    path('excess-bottle-counts/', excess_bottle_count_list, name='excess_bottle_count_list'),
    path('excess-bottle-counts/new/', excess_bottle_count_create, name='excess_bottle_count_create'),
    path('excess-bottle-counts/<uuid:pk>/edit/', excess_bottle_count_update, name='excess_bottle_count_update'),
    path('excess-bottle-counts/<uuid:pk>/delete/', excess_bottle_count_delete, name='excess_bottle_count_delete'),

    path('salesman_customer_request_type_list', SalesmanCustomerRequestType_List.as_view(), name='salesman_customer_request_type_list'),
    path('salesman_customer_request_create',SalesmanCustomerRequestType_Create.as_view(), name='salesman_customer_request_create'),
    path('salesman_customer_requesttype_edit/<str:pk>', SalesmanCustomerRequestType_Edit.as_view(), name='salesman_customer_requesttype_edit'),
    path('salesman_customer_requesttype_delete/<uuid:pk>/', SalesmanCustomerRequestType_Delete.as_view(), name='salesman_customer_requesttype_delete'),

    path('salesman_customer_requests_list/', salesman_customer_requests_list, name='salesman_customer_requests_list'),
    path('update_request_status/<uuid:pk>/', update_request_status, name='update_request_status'),

    path('audit_report/', audit_report, name='audit_report'),
    path('audit_detail/<uuid:audit_id>/', audit_detail, name='audit_detail'),
    
    path('freelancevan',freelancevan, name='freelancevan'),
    
    path('freelancevan_rate_change/<str:pk>/', FreelanceVanRateHistoryView.as_view(), name='freelancevan_rate_change'),
    re_path(r'^freelance_other_product_rate_change/(?P<pk>.*)/$',  FreelanceVanOtherProductRateChangeView.as_view(), name='freelance_other_product_rate_change'),
    
    path('freelance_van_bottle_issue/<uuid:van_id>/',freelance_van_bottle_issue, name='freelance_van_bottle_issue'),
    path('freelancevan_outstanding_details/<uuid:van_id>/', freelance_van_outstanding_details, name='freelancevan_outstanding_details'),
    path('freelance_van_issue_report/', freelance_van_issue_report, name='freelance_van_issue_report'),
    path('freelance_van_issue_list/<uuid:van_id>/', freelance_van_issue_list, name='freelance_van_issue_list'),
    

]