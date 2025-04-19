from django.urls import path, include
from . import views
from .masterfiles import masters
from .masterfiles import filterfields
from .purchasefiles import purchase
from .saleorderfiles import saleorder
from .invoicefiles import invoice
from .inventoryfiles import inventory
from .dashboardfiles import dashboard
from .analyticsfiles import analytics

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('get_distributor_name/', views.get_distributor_name, name='get_distributor_name'),
    path('get_current_state/', filterfields.get_current_state, name='get_current_state'),
    path('get_current_state_dropdown_options/', views.get_current_state_dropdown_options, name='get_current_state_dropdown_options'),
    path('get_distributor_display_name/', views.get_distributor_display_name, name='get_distributor_display_name'),
    path('get_session/', views.get_session, name='get_session'),
    path('set_session/', views.set_session, name='set_session'),
    path('clear_session/', views.clear_session_parameters, name='clear_session'),
    path('testdashboard/', views.testdashboard, name='testdashboard'),  # Test Dashboard
    #path('', views.user_login, name='user_login'),  # Root URL
    path('login/', views.login, name='login'),  # Login page accessible at /login/
    path('dmsdashboard/', views.dmsdashboard, name='dmsdashboard'),  # Main Dashboard
    path('sales/', views.sales_data, name='sales_data'),  # API for sales data
    path('purchase/', views.purchase_data, name='purchase_data'),  # API for purchase data

    # Specific report pages
    path('reports/', views.reports, name='reports'),  # Reports overview (with cards)
    path('analytics/', views.analytics, name='analytics'),

    # Report detail views for individual report types
    path('reports/stock/daily/', views.daily_stock_report, name='daily_stock_report'),


    # Django authentication system URLs
    path('accounts/', include('django.contrib.auth.urls')),

    #Masters html pages
    path('reports/masters/customers/', masters.customers, name='customers'),
    path('reports/masters/products/', masters.products, name='products'),
    #path('reports/masters/vendors/', masters.vendors, name='vendors'),

    path('get_distributor_dropdown_options/', filterfields.get_distributor_dropdown_options, name='get_distributor_dropdown_options'),
    path('get_group1_dropdown_options/', filterfields.get_group1_dropdown_options, name='get_group1_dropdown_options'),
    path('get_stock_report_dropdown_options/', filterfields.get_stock_report_dropdown_options, name='get_stock_report_dropdown_options'),
    path('get_product_distributor_dropdown_options/', filterfields.get_product_distributor_dropdown_options, name='get_product_distributor_dropdown_options'),
    path('get_product_dropdown_options/', filterfields.get_product_dropdown_options, name='get_product_dropdown_options'),
    path('get_product_category_dropdown_options/', filterfields.get_product_category_dropdown_options, name='get_product_category_dropdown_options'),
    path('get_product_division_dropdown_options/', filterfields.get_product_division_dropdown_options, name='get_product_division_dropdown_options'),
    path('get_product_brand_dropdown_options/', filterfields.get_product_brand_dropdown_options, name='get_product_brand_dropdown_options'),
    path('get_product_state_dropdown_options/', filterfields.get_product_state_dropdown_options, name='get_product_state_dropdown_options'),

    #Masters Json Data
    path('customers_report/', masters.customers_report, name='customers_report'),
    path('product_report/', masters.product_report, name='product_report'),
    #path('reports/masters/products/', masters.product_report, name='product_report'),
    path('reports/masters/vendors/', masters.vendor_report, name='vendor_report'),

    #Purchase html pages
    path('reports/purchase/purchase_order/', purchase.purchase_order, name='purchase_order'),
    path('reports/purchase/purchase_return/', purchase.purchase_return, name='purchase_return'),
    path('reports/purchase/purchase_receipt/', purchase.purchase_receipt, name='purchase_receipt'),

    #Purchase Json Data
    path('purchase_order_report/', purchase.purchase_order_report, name='purchase_order_report'),
    path('purchase_return_report/', purchase.purchase_return_report, name='purchase_return_report'),
    path('purchase_receipt_report/', purchase.purchase_receipt_report, name='purchase_receipt_report'),

    #Sales html pages
    path('reports/invoice/sales_invoice/', invoice.sales_invoice, name='sales_invoice'),
    path('reports/invoice/sales_return/', invoice.sales_return, name='sales_return'),

    #Sales Json Data
    path('sales_invoice_report/', invoice.sales_invoice_report, name='sales_invoice_report'),
    path('sales_return_report/', invoice.sales_return_report, name='sales_return_report'),

    #SaleOrder html pages
    path('reports/invoice/sales_invoice/', invoice.sales_invoice, name='sales_invoice'),
    path('reports/invoice/sales_return/', invoice.sales_return, name='sales_return'),

    #SaleOrder Json Data
    path('sale_order_report/', saleorder.sale_order_report, name='sale_order_report'),
    path('sale_order_pending_report/', saleorder.sale_order_pending_report, name='sale_order_pending_report'),

    #Inventory html pages
    path('reports/stock/report/', inventory.stock_report, name='stock_report'),

    #Inventory Json Data
    path('stock_data/', inventory.stock_data, name='stock_data'),


    #Dashboard Summary Card Data
    path('sale_summary_card/', dashboard.sale_summary_card, name='sale_summary_card'),
    path('purchase_summary_card/', dashboard.purchase_summary_card, name='purchase_summary_card'),
    path('stock_summary_card/', dashboard.stock_summary_card, name='stock_summary_card'),
    path('invoice_summary/', dashboard.invoice_summary, name='invoice_summary'),
    path('saleorder_summary/', dashboard.saleorder_summary, name='saleorder_summary'),
    #Charts Json
    path('monthly_sales_data/', analytics.monthly_sales_data, name='monthly_sales_data'),
    path('monthly_sales_table_chart/', analytics.monthly_sales_table_chart, name='monthly_sales_table_chart'),


    #Analytic Charts Html
    path('sales_chart/', analytics.sales_chart, name='sales_chart'),
    path('purchase_chart/', analytics.purchase_chart, name='purchase_chart'),    
    path('stock_chart/', analytics.stock_chart, name='stock_chart'),

    
    path('sales_qty_pivot/', analytics.sales_qty_pivot, name='sales_qty_pivot'),
    path('sales_value_pivot/', analytics.sales_value_pivot, name='sales_value_pivot'),
    path('sales_summary_pivot/', analytics.sales_summary_pivot, name='sales_summary_pivot'),

    path('sales_qty_pivot_view/', analytics.sales_qty_pivot_view, name='sales_qty_pivot_view'),
    path('sales_value_pivot_view/', analytics.sales_value_pivot_view, name='sales_value_pivot_view'),
    path('sales_summary_pivot_view/', analytics.sales_summary_pivot_view, name='sales_summary_pivot_view'),

    #Analytic Charts Json    
    path('analytics_monthly_sales_data/', analytics.analytics_monthly_sales_data, name='analytics_monthly_sales_data'),


    #path('get_chart_data/<str:report_type>/', analytics.get_chart_data, name='get_chart_data'),
    path("get_chart_data/<str:report_type>/", analytics.get_chart_data, name="get_chart_data"),
    #path('get_chart_stock_data/<str:report_type>/', analytics.get_chart_stock_data, name='get_chart_stock_data'),
    path('get_stock_chart_data/<str:report_type>/', analytics.get_stock_chart_data, name='get_stock_chart_data'),
]
