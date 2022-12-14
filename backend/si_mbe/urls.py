from django.urls import path
from si_mbe import views


urlpatterns = [
     path('', views.Home.as_view(), name='homepage'),
     path('sparepart/find/', views.SearchSparepart.as_view(), name='search_sparepart'),
     path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
     path('dashboard/sparepart/', views.SparepartDataList.as_view(), name='sparepart_data_list'),
     path('dashboard/sparepart/add/', views.SparepartDataAdd.as_view(), name='sparepart_data_add'),
     path('dahsboard/sparepart/edit/<int:sparepart_id>', views.SparepartDataUpdate.as_view(),
          name='sparepart_data_update'),
     path('dahsboard/sparepart/delete/<int:sparepart_id>', views.SparepartDataDelete.as_view(),
          name='sparepart_data_delete'),
     path('dashboard/sales/', views.SalesList.as_view(), name='sales_list'),
     path('dashboard/sales/add/', views.SalesAdd.as_view(), name='sales_add'),
     path('dashboard/sales/edit/<int:sales_id>', views.SalesUpdate.as_view(), name='sales_update'),
     path('dashboard/sales/delete/<int:sales_id>', views.SalesDelete.as_view(), name='sales_delete'),
     path('dashboard/restock/', views.RestockList.as_view(), name='restock_list'),
     path('dashboard/restock/add/', views.RestockAdd.as_view(), name='restock_add'),
     path('dashboard/restock/edit/<int:restock_id>', views.RestockUpdate.as_view(), name='restock_update'),
     path('dashboard/restock/delete/<int:restock_id>', views.RestockDelete.as_view(), name='restock_delete'),
     path('dashboard/supplier/', views.SupplierList.as_view(), name='supplier_list'),
     path('dashboard/supplier/add/', views.SupplierAdd.as_view(), name='supplier_add'),
     path('dashboard/supplier/edit/<int:supplier_id>', views.SupplierUpdate.as_view(), name='supplier_update'),
     path('dashboard/supplier/delete/<int:supplier_id>', views.SupplierDelete.as_view(), name='supplier_delete'),
     path('report/sales/', views.SalesReportList.as_view(), name='sales_report_list'),
     path('report/sales/<int:sales_id>', views.SalesReportDetail.as_view(), name='sales_report_detail'),
]
