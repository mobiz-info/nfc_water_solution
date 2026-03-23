from django.conf import settings
from django.urls import path,re_path
from django.conf.urls.static import static

from .views import *
from .views import StaffIssueOrdersNFCAPIView, OrderDamageNFCAPIView, EmptyBottleAllocationNFCAPIView
import bottle_management.views as bottle_views
from master.views import privacy, terms_and_conditions
from client_management.views import CustomerCreditAPI


from . views import *
from . import views

urlpatterns = [

    ########################## Account ########################
    path('register/',UserSignUpView.as_view()),
    path('register/<int:id>/',UserSignUpView.as_view()),
    path('login/',Login_Api.as_view()),
    # Customer Sign in
    path('customers/',Customer_API.as_view()),
    path('customers/<str:id>/',Customer_API.as_view()),
    path('customers-delete-request/',CustomerAccountDeleteRequestView.as_view()),
    
    path('customer-login/',CustomerLoginApi.as_view()),
    path('customer-next-visit-date/',NextVisitDateAPI.as_view()),
    path('customer-coupon-balance/',CustomerCouponBalanceAPI.as_view()),
    path('customer-outstanding-balance/',CustomerOutstandingAPI.as_view()),
    
    path('store-keeper-login/',StoreKeeperLoginApi.as_view()),
    path('marketing-executive-login/',MarketingExecutiveLoginApi.as_view()),
    
    #################Master Url##############################

    path('route/<str:id>/',RouteMaster_API.as_view()),
    path('route/',RouteMaster_API.as_view())  ,

    path('location/<str:id>/',LocationMaster_API.as_view()),
    path('location/',LocationMaster_API.as_view()) ,

    path('designation/<str:id>/',DesignationMaster_API.as_view()),
    path('designation/',DesignationMaster_API.as_view()),

    path('branch/<str:id>/',BranchMaster_API.as_view()),
    path('branch/',BranchMaster_API.as_view()),

    path('category/<str:id>/',CategoryMaster_API.as_view()),
    path('category/',CategoryMaster_API.as_view()),

    path('emirates/<str:id>/',EmirateMaster_API.as_view()),
    path('emirates/',EmirateMaster_API.as_view()),

    ###################Product Url#######################

    path('product/',Product_API.as_view()),
    path('product/<str:id>/',Product_API.as_view()),
    path('product_price/',Product_Default_Price_API.as_view()),
    path('product_price/<str:id>/',Product_Default_Price_API.as_view()),

    #######################Van Url#################################

    path('van/',Van_API.as_view()),
    path('van/<str:id>/',Van_API.as_view()),
    path('assign_route/',Route_Assign.as_view()),

    path('schedule_by_route/<str:route_id>/<str:date_str>/<str:trip>', ScheduleByRoute.as_view()),
    path('schedule_view/<str:date_str>/', ScheduleView.as_view()),


    path('expense_heads/', ExpenseHeadListAPI.as_view(), name='expensehead-list'),
    path('expense_heads/<uuid:pk>/', ExpenseHeadDetailAPI.as_view(), name='expensehead-detail'),

    path('expenses/', ExpenseListAPI.as_view(), name='expense-list'),
    path('expenses/<uuid:expense_id>/', ExpenseDetailAPI.as_view(), name='expense-detail'),

    # Order change and return
    path('change_reason/', ChangeReasonListAPI.as_view(), name='change_reason'),
    path('change_reason/<int:change_reason_id>', ChangeReasonDetailAPI.as_view(), name="change_reason_detai"),

    path('order_change/', OrderChangeListAPI.as_view(), name='order_change'),
    path('order_change/<uuid:order_change_id>', OrderChangeDetailAPI.as_view(), name="order_change_detai"),

    path('order_return/', OrderReturnListAPI.as_view(), name='order_return'),
    path('order_return/<uuid:order_return_id>', OrderReturnDetailAPI.as_view(), name="order_return_detai"),  

    
    ####################### Customer_Url s#################################

    path('customer_custody_item/',Customer_Custody_Item_API.as_view()),

    ##############################Van app####################################

    # Staff punch in and punch out
    path('staff_punch_in_api/', PunchIn_Api.as_view(), name='staff_punch_in_api'),
    path('staff_punch_out_api/', PunchOut_Api.as_view(), name='staff_punch_out_api'),
    path('location_emirates/', location_based_on_emirates, name='location-based-on-emirates'),
    path('emirates-based-locations/', emirates_based_locations, name='emirates_based_locations'),
    path('staff_assigned_routes/',Route_Assign_Staff_Api.as_view(), name='staff_assigned_routes'),
    path('create/customer/',Customer_API.as_view()),
    path('create/customer/<str:id>/',Customer_API.as_view()),
    path('get_items_api/',Get_Items_API.as_view()),
    path('get_items_api/<str:id>/',Get_Items_API.as_view()),
    path('add_custody_item/',Add_Customer_Custody_Item_API.as_view()),
    path('add_custody_item/<str:id>/',Add_Customer_Custody_Item_API.as_view()),
    path('add_no_of_coupons/', Add_No_Coupons.as_view()),
    path('add_no_of_coupons/<str:id>/', Add_No_Coupons.as_view()),
    
    # supply
    re_path(r'^supply-product/', supply_product.as_view()),
    # re_path(r'^create-customer-supply/$', create_customer_supply.as_view()),
    path('create-customer-supply/', create_customer_supply_latest),
    path('edit-customer-supply/<uuid:pk>/', edit_customer_supply.as_view()),
    # path('delete-customer-supply/<uuid:pk>/', delete_customer_supply.as_view()),
    re_path(r'^customer-outstanding/$', customer_outstanding.as_view()),
    # path('create-customer-supply-latest/', create_customer_supply_latest),
    path('create-customer-supply-nfc/', create_customer_supply_nfc),
   
    ################### COUPON MANAGEMENT URL ######################
    path('couponType/',CouponType_API.as_view()),
    path('couponType/<str:id>',CouponType_API.as_view()),
    path('coupon/',Coupon_API.as_view()),
    path('coupon/<str:id>',Coupon_API.as_view()),
    path('couponRequest/',CouponRequest_API.as_view()),
    path('assignStaffCoupon/',AssignStaffCoupon_API.as_view()),
    path('assignToCustomer/',AssigntoCustomer_API.as_view()),
    
    # coupon recharge
    path('get-lower-coupon-customers/', views.get_lower_coupon_customers),
    path('fetch-coupon-data/', views.fetch_coupon),
    path('customer-coupon-recharge/', CustomerCouponRecharge.as_view()),
    
    path('customer-coupon-stock/', customerCouponStock.as_view()),
    
    path('product-items/', views.product_items),
    path('staff_new_order_api/', Staff_New_Order.as_view()),
    path('customer_create/',Customer_Create.as_view()),
    path('customer_details/<str:id>/',CustomerDetails.as_view()),
    path('check_customer', Check_Customer.as_view(), name='check_customer'),
    path('verify_otp', Verify_otp.as_view(), name='verify_otp'),

    # client_management
    path('vacations/', VacationListAPI.as_view(), name='vacation_list_api'),
    path('vacations/add/', VacationAddAPI.as_view(), name='vacation_add_api'),
    path('vacations/<uuid:vacation_id>/', VacationEditAPI.as_view(), name='vacation_edit_api'),
    path('vacations/<uuid:vacation_id>/delete/', VacationDeleteAPI.as_view(), name='vacation_delete_api'),
    
    path('myclient/',Myclient_API.as_view()),

    #custody items
    path('get_products/', GetProductAPI.as_view(), name='get_products'),
    path('add_custody_items/', CustodyCustomAPIView.as_view(), name='custody_item_add'),
    path('custody_item_list/' ,CustodyCustomItemListAPI.as_view(), name='custody_item_list'),
    path('bottle_status_customers/', BottleStatusCustomerFilterAPIView.as_view(), name='bottle_status_customers'),
    path('custody_item_return/', CustodyItemReturnAPI.as_view(), name='custody_item_return'),

    path('outstanding_amount/',OutstandingAmountAPI.as_view(), name = 'outstanding_amount'),
    path('outstanding_amount_list/',OutstandingAmountListAPI.as_view(), name = 'outstanding_amount_list'),
    # path('outstanding_coupon/',OutstandingCouponAPI.as_view(), name = 'outstanding_coupon'),

    path('vanstock-list/', VanStockAPI.as_view()),
    
    # path('api/coupon_count/<uuid:pk>/', CouponCountListAPI.as_view(), name='coupon_count_list_api'),
    # path('check_customer_existence/', check_customer_existence, name='check_customer_existence'),
    # path('coupon_count/<uuid:pk>/', CouponCountList.as_view(), name='coupon_count_list_api'),
    # path('coupon_count/<uuid:pk>/', CouponCountListAPI.as_view(), name='coupon_count_list_api'),
    path('add_new_coupon/<uuid:pk>/', NewCouponCountAPI.as_view(), name='api_new_coupon_count'),
    path('delete_coupon_count/<uuid:pk>/', DeleteCouponCount.as_view(), name='delete_coupon_count'),
    path('customers_coupon/', CustomerCouponListAPI.as_view(), name='customer_list_api'),

    path('collectionapi/', CollectionAPI.as_view(), name='collectionapi'),
    path('customer_credit_api/', CustomerCreditAPI.as_view(), name='customer_credit_api'),
    path('add_collection_payment/', AddCollectionPayment.as_view(), name='add_collection_payment'),

    path('product-bottle/', ProductAndBottleAPIView.as_view(), name='product_bottle_api'),
    
    path('coupon-types/', CouponTypesAPI.as_view(), name='coupon_types'),



    path('emergency_customers/', EmergencyCustomersAPI.as_view(), name='emergency_customers'),

    #--------------------New sales Report -------------------------------
    path('customer_sales_report_api/', CustomerSalesReportAPI.as_view(), name='customer_sales_report'),

    path('creditnote/', CreditNoteAPI.as_view(), name='creditnote'),
    
    path('dashboard/<uuid:route_id>/<str:trip>/', DashboardAPI.as_view(), name='dashboard'),
    path('collectionreport/', CollectionReportAPI.as_view(), name='collectionreport'),

    path('coupon_supply_count/<int:salesman_id>/', CouponSupplyCountAPIView.as_view(), name='coupon_supply_count'),
    path('coupon_sales_count/<int:salesman_id>/', Coupon_Sales_APIView.as_view(), name='coupon_sales_count'),

    path('redeemed_history/', RedeemedHistoryAPI.as_view(), name='redeemed_history'),

    # path('visit_report/', VisitReportAPI.as_view(), name='visit_report'),
    path('coupon_consumption_report/', CouponConsumptionReport.as_view(), name='coupon_consumption_report'),
    path('stockmovementreport/<str:salesman_id>/', StockMovementReportAPI.as_view(), name='stock_movement_report'),
    
    path('visit_report/', VisitReportAPI.as_view(), name='visit_report'),
    path('nonvisited_report/', NonVisitedReportAPI.as_view(), name='nonvisited_report'),

    path('customer_statement/', CustomerStatementReport.as_view(), name='customer-customer_statement'),
    
    path('salesman-expenses/', ExpenseReportAPI.as_view(), name='salesman_expences'),
    path('dsr-cashsales/', CashSaleReportAPI.as_view(), name='cash_sale_report'),
    path('dsr-creditsales/', CreditSaleReportAPI.as_view(), name='credit_sale_report'),

    path('dsr-visit_statistics/', VisitStatisticsAPI.as_view(), name='visit_statistics'),
    path('dsr-fivegallon_related/', FivegallonRelatedAPI.as_view(), name='fivegallon_related'),
    
    path('shop-in/<uuid:customer_pk>/', ShopInAPI.as_view(), name='shop_in'),
    path('shop-out/<uuid:customer_pk>/', ShopOutAPI.as_view(), name='shop_out'),
    
    path('salesman-request/', SalesmanRequestAPI.as_view(), name='salesman_request'),
    
    path('tax/', TaxAPI.as_view(), name='tax_api'),
    
    path('competitors/', CompetitorsAPIView.as_view(), name='competitors'),
    path('competitors_list/', CompetitorsListAPIView.as_view(), name='competitors_list'),
    path('market_share/',MarketShareAPI.as_view(), name='market_share'),
    # path('offload_coupon/', OffloadCouponAPI.as_view(), name='offload_coupon'),
    
    path('pending-supply-report/<str:route_id>/', PendingSupplyReportView.as_view(), name='pending-supply-report'),
    
    path('bottle_stock/', BottleStockView.as_view(), name='bottle_stock'),
    path('freshcanandemptybottle/', FreshcanEmptyBottleView.as_view(), name='freshcanandemptybottle'),
    path('custody_report_view/', CustodyReportView.as_view(), name='custody_report_view'),

    path('freshcan_Vs_Coupon/', FreshcanVsCouponView.as_view(), name='freshcan_Vs_Coupon'),
    
    path('customer-orders/', CustomerOrdersAPIView.as_view(), name='customer_orders'),   
    path('water_bottle_purchases/', WaterBottlePurchaseAPIView.as_view(), name='water_bottle_purchases'),
    path('custody_customer_view/', CustodyCustomerView.as_view(), name='custody_customer_view'),


    path('production/', ProductListAPIView.as_view(), name='product-list'),
    path('production/create/', ProductCreateAPIView.as_view(), name='product-create'),
    
    path('dispensers-coolers-purchases/', DispensersAndCoolersPurchasesAPIView.as_view(), name='dispensers-coolers-purchases'),
    path('customer-coupon-purchase/', CustomerCouponPurchaseView.as_view(), name='customer-coupon-purchase'),

    path('stock_movement/', StockMovementCreateAPI.as_view(), name='stock-movement-create'),
    path('stock_movement_details/', StockMovementDetailsAPIView.as_view(), name='stock-movement-details'),
    path('nonvisitreason/', NonVisitReasonAPIView.as_view(), name='nonvisitreason'),
    
    path('complaints_create/', CustomerComplaintCreateView.as_view(), name='create-complaint'),
    path('nonvisit_report/', NonVisitReportCreateAPIView.as_view(), name='nonvisit_report'),
    
    path('send_device_token/', Send_Device_API.as_view(),name='send_device_token'),
    path('send_customer_device_token/', CustomerDeviceTokenAPI.as_view(),name='send_customer_device_token'),
    
    path('customer_Wise_Coupon_sale/', CustomerWiseCouponSaleAPIView.as_view(),name='customer_Wise_Coupon_sale'),
    path('total_coupon_consumed/', TotalCouponsConsumedView.as_view(), name='total_coupon_consumed'),

    path('edit-product/', EditProductAPIView.as_view(), name='edit-product'),
    path('offload-coupons/', GetVanCouponBookNoAPIView.as_view(), name='offload-coupon-list'),
    path('edit-coupon/<str:pk>/', EditCouponAPIView.as_view(), name='edit-coupon'),
    
    # path('salsman-request/', SalesmanRequestAPIView.as_view(), name='salsman-request'),
    

    path('coupons-products/', CouponsProductsAPIView.as_view(), name='coupons_products'),
    path('potential_buyers/', PotentialBuyersAPI.as_view(), name='potential_buyers'),

    path('get_notification/',Get_Notification_APIView.as_view(), name='get_notification'),
    

    # offload request apis start
    path('offloads-requesting/', OffloadRequestingAPIView.as_view(), name='offload_request'),
    
    # offload request apis end
    
    #offload store app 
    path('offloadrequest_vanlist/', OffloadRequestVanListAPIView.as_view(), name='offloadrequest_vanlist'),

    path('offloads/', OffloadRequestListAPIView.as_view(), name='api_offload'),
    path('offload_requests_productlist/<uuid:van_id>/', OffloadRequestListAPIView.as_view(), name='offload_requests_productlist'),
    
    
    # path('api_staffIssueOrdersCreate/<str:staff_order_details_id>/', StaffIssueOrdersAPIView.as_view(), name='api_staffIssueOrdersCreate'),
    # path('api_staffIssueOrdersCreate/create/<str:staff_order_details_id>/', StaffIssueOrdersAPIView.as_view(), name='api_staffIssueOrders_Create'),
    
    #------------------------------------Store Appp Orders Api-----------------------------------------------------
    path('api_staff_issue_orders_list/', StaffIssueOrdersListAPIView.as_view(), name='api_staff_issue_orders_list'),
    path('api_staffIssueOrdersCreate/<uuid:staff_order_id>/', StaffIssueOrdersAPIView.as_view(), name='api_staffIssueOrdersCreate'),
    path('get_coupon_bookno/', GetCouponBookNoView.as_view(), name='get_coupon_bookno'),
    path('approve-order/<uuid:order_id>/', ApproveOrderAPIView.as_view(), name='approve_order'),
    
    path('onload-van/', VanOnloadAPIView.as_view(), name='van_onload'),
    path('onload-van-production/', VanOnloadProductionAPIView.as_view(), name='van_onload_production'),
    #------------------------------------Store Appp Orders Api Completes-----------------------------------------------------
    #------------------------------------Location Api -----------------------------------------------------

    path('location_updates/', LocationUpdateAPIView.as_view(), name='location_updates'),
    #------------------------------------Van Stock Api -----------------------------------------------------
    path('van_list/', VanListView.as_view(), name='van_list'),
    path('van_detail/<uuid:van_id>/', VanDetailView.as_view(), name='van_detail'),
    #---------------------------store app product stock-------------- 
    path('product-stocks/', ProductStockListAPIView.as_view(), name='product-stock-list'),
    #---------------------------Salesman app report ------------------------------------------------   
    path('cash_sales_report/', CashSalesReportAPIView.as_view(), name='cash_sales_report'),
    path('credit_sales_report/', CreditSalesReportAPIView.as_view(), name='credit_sales_report'),
    #---------------------------Bottle Count Store App Url ------------------------------------------------   
    path('api_van_route_bottle_count/', VanRouteBottleCountView.as_view(), name='api_van_route_bottle_count'),
    path('api_vans_route_bottle_count_add/<uuid:pk>/', VansRouteBottleCountAddAPIView.as_view(), name='api_vans_route_bottle_count_add'),
    path('api_vans_route_bottle_count_deduct/<uuid:pk>/', VansRouteBottleCountDeductAPIView.as_view(), name='api_vans_route_bottle_count_deduct'),
    #-------------Store app stock transfer-----------------------------------------
    path('stock_transfer/', StockTransferAPIView.as_view(), name='stock_transfer'),
    
    path('scrap_stock/', ScrapStockAPIView.as_view(), name='scrap_stock'),
    path('add-damage-bottle/', addDamageBottleAPIView.as_view(), name='add_damage_bottle'),
    
    path('production-damage-choices/', ProductTransferChoicesAPI.as_view(), name='production_damage_choices'),
    path('production-damage/', ProductionDamageAPIView.as_view(), name='production_damage'),
    
    path('vansale-damage/', VanSaleDamageAPIView.as_view(), name='vansale_damage'),
    
    path('customer-product-return/', CustomerProductReturnAPIView.as_view(), name='customer_product_return'),
    path('customer-product-replacement/', CustomerProductReplaceAPIView.as_view(), name='customer_product_replacement'),
    
    path('excess-bottle-count/', ExcessBottleCountAPIView.as_view(), name='excess_bottle_count'),

    path('privacy-policy/', privacy),
    
    path('terms_and_conditions/', terms_and_conditions),
    path('customers_coupons/<uuid:customer_id>/', CustomerCouponListAPIView.as_view(), name='customer-coupon-list'),
    
    path('credit-note-list/', CreditNoteListAPI.as_view(), name='credit_note_list'),
    path('product-route-salesreport/', ProductRouteSalesReportAPIView.as_view(), name='product_route_salesreport_api'),
    
    path('sales-invoices/', SalesInvoicesAPIView.as_view(), name='sales_invoices'),
    path('customer-supply-list/', CustomerSupplyListAPIView.as_view(), name='customer-supply-list'),
    
    path('customer-cart/', CustomerCartAPIView.as_view(), name='customer_cart'),
    
    path('customer-outstandings-amount-report/', CustomersOutstandingAmountsAPI.as_view(), name='customers_outstandings_amount_reports'),
    path('customer-outstandings-bottles-report/', CustomersOutstandingBottlesAPI.as_view(), name='customers_outstandings_bottles_reports'),
    path('customer-outstandings-coupon-report/', CustomersOutstandingCouponsAPI.as_view(), name='customers_outstandings_coupons_reports'),
    
    path('salesman/', SalesmanListAPIView.as_view(), name='salesman-list'),
    
    ############################# Customer App ##############################################
    path('customer-registration-request/', CustomerRegistrationRequestView.as_view(), name='customer_registration_request'),
    
    path('marketing_executive_salesmen/', MarketingExecutiveSalesmanListAPIView.as_view(), name='marketing_executive_salesmen'),
    
    
    path('customer-lead/',LeadCustomersView.as_view(), name='customer_lead_api'),
    path('customer-lead-cancel-reasons/',LeadCustomersCancelReasonsView.as_view(), name='customer_lead_cancel_reason'),
    path('customer-lead-update-status/',LeadCustomersUpdateStatusView.as_view(), name='customer_lead_update_status'),

    path('damage-control/', DamageControlAPIView.as_view(), name='damage_control'),
    path('customer-request-types/', CustomerRequestTypeAPIView.as_view(), name='customer_request_types_list'),
    path('customer-request-types/<uuid:id>/', CustomerRequestTypeAPIView.as_view(), name='customer_request_type_detail'),
    
    path('customer-requests/', CustomerRequestCreateAPIView.as_view(), name='customer_request_create'),
    path('customer-requests-lists/', CustomerRequestListAPIView.as_view(), name='customer_request_list'),
    
    path('update-customer-request-status/', UpdateCustomerRequestStatusView.as_view(), name='update-customer-request-status'),
    path('all-customer-requests-lists/', AllCustomerRequestListAPIView.as_view(), name='all-customer-requests-lists'),


    path('salesman-customer-request-types/', SalesmanCustomerRequestTypeAPIView.as_view()),
    path('salesman-customer-requests/', SalesmanCustomerRequestCreateAPIView.as_view()),
    path('salesman-customer-requests-lists/', SalesmanCustomerRequestListAPIView.as_view()),
    path('update-salesman-customer-request-status/<uuid:request_id>/', UpdateSalesmanCustomerRequestStatusView.as_view()),
    path('all-salesman-customer-requests-lists/', AllSalesmanCustomerRequestListAPIView.as_view()),
    #-----------------------------Auditing--------------------------------------------
    path('audit-list/', AuditListAPIView.as_view(), name='audit-list'),
    path('audit-details/<uuid:audit_id>/', AuditDetailListAPIView.as_view(), name='audit-details'),
    path('start-audit/', StartAuditAPIView.as_view(), name='start-audit'),
    path('end-audit/<uuid:audit_id>/', EndAuditAPIView.as_view(), name='end-audit'),
    path('create-audit-detail/', CreateAuditDetailAPIView.as_view(), name='create-audit-detail'),
    
    path('production-onload-report/', ProductionOnloadReportAPIView.as_view(), name='production_onload_report_api'),
    path('scrap-clearence-report/', ScrapClearanceReportAPIView.as_view(), name='scrap_clearence_report_api'),
    
    path('overview/', OverviewAPIView.as_view(), name='overview-api'),
    path('sales-dashboard/', SalesDashbordAPIView.as_view(), name='sales-dashboard'),
    path('bottle-statistics-dashboard/', BottleStatisticsDashboardAPIView.as_view(), name='bottle-statistics-dashboard'),
    path('coupon-overview-dashboard/', CouponDashboardAPIView.as_view(), name='coupon-overview-dashboard'),
    path('customer-statistics-dashboard/', CustomerStatisticsDashboardAPIView.as_view(), name='customer-statistics-dashboard'),
    path('others-dashboard/', OthersDashboardAPIView.as_view(), name='others-dashboard'),
    path('today-collection-dashboard/', TodayCollectionAPIView.as_view(), name='today-collection-dashboard'),
    path('old-collections/', OldCollectionAPIView.as_view(), name='old-collections'),
    path('total-collections/', TotalCollectionAPIView.as_view(), name='total-collections'),
    
    
    path('reprint-invoices/', ReprintInvoicesAPIView.as_view(), name='reprint-invoices'),

    # NFC Mapping
    path('get_available_bottles/', bottle_views.get_available_bottles, name='get_available_bottles'),
    path('nfc_mapping_save/', bottle_views.nfc_mapping_save, name='nfc_mapping_save'),
    path('generate_bottles_with_nfc/', bottle_views.generate_bottles_with_nfc_api, name='generate_bottles_with_nfc'),
    path('preview_bottles/', bottle_views.preview_bottles, name='preview_bottles'),
    path('get_bottle_by_nfc/', bottle_views.get_bottle_details_by_nfc, name='get_bottle_details_by_nfc'),
    path('get_bottle_by_qr/', bottle_views.get_bottle_by_qr, name='get_bottle_by_qr'),
    path('get_van_by_route/', bottle_views.get_van_by_route, name='get_van_by_route'),
    path('transfer_bottles_to_van/', bottle_views.transfer_bottles_to_van, name='transfer_bottles_to_van'),
    path('refill_bottles/', bottle_views.refill_bottles, name='refill_bottles'),
    path('check_bottle_in_van/', bottle_views.check_bottle_in_van, name='check_bottle_in_van'),
    path('api_staffIssueOrdersCreateNFC/', StaffIssueOrdersNFCAPIView.as_view(), name='api_staffIssueOrdersCreateNFC'),
    path('order-damage-nfc/', OrderDamageNFCAPIView.as_view(), name='order_damage_nfc'),
    path('empty-bottle-allocation-nfc/', EmptyBottleAllocationNFCAPIView.as_view(), name='empty_bottle_allocation_nfc'),

]
