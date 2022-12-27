from django.urls import path
from si_mbe import views


urlpatterns = [
     path('', views.Home.as_view(), name='homepage'),
     path('sparepart/find/', views.SearchSparepart.as_view(), name='search_sparepart'),

     # Admin endpoint access
     path('admin/', views.AdminDashboard.as_view(), name='admin_dashboard'),
     path('admin/sparepart/', views.SparepartDataList.as_view(), name='sparepart_data_list'),
     path('admin/sparepart/add/', views.SparepartDataAdd.as_view(), name='sparepart_data_add'),
     path('admin/sparepart/edit/<int:sparepart_id>/', views.SparepartDataUpdate.as_view(),
          name='sparepart_data_update'),
     path('admin/sparepart/delete/<int:sparepart_id>/', views.SparepartDataDelete.as_view(),
          name='sparepart_data_delete'),
     path('admin/sales/', views.SalesList.as_view(), name='sales_list'),
     path('admin/sales/add/', views.SalesAdd.as_view(), name='sales_add'),
     path('admin/sales/edit/<int:sales_id>/', views.SalesUpdate.as_view(), name='sales_update'),
     path('admin/sales/delete/<int:sales_id>/', views.SalesDelete.as_view(), name='sales_delete'),
     path('admin/restock/', views.RestockList.as_view(), name='restock_list'),
     path('admin/restock/add/', views.RestockAdd.as_view(), name='restock_add'),
     path('admin/restock/edit/<int:restock_id>/', views.RestockUpdate.as_view(), name='restock_update'),
     path('admin/restock/delete/<int:restock_id>/', views.RestockDelete.as_view(), name='restock_delete'),
     path('admin/supplier/', views.SupplierList.as_view(), name='supplier_list'),
     path('admin/supplier/add/', views.SupplierAdd.as_view(), name='supplier_add'),
     path('admin/supplier/edit/<int:supplier_id>/', views.SupplierUpdate.as_view(), name='supplier_update'),
     path('admin/supplier/delete/<int:supplier_id>/', views.SupplierDelete.as_view(), name='supplier_delete'),
     path('admin/service/', views.ServiceList.as_view(), name='service_list'),
     path('admin/service/add/', views.ServiceAdd.as_view(), name='service_add'),
     path('admin/service/edit/<int:service_id>/', views.ServiceUpdate.as_view(), name='service_update'),
     path('admin/service/delete/<int:service_id>/', views.ServiceDelete.as_view(), name='service_delete'),
     path('admin/storage/', views.StorageList.as_view(), name='storage_list'),
     path('admin/storage/add/', views.StorageAdd.as_view(), name='storage_add'),
     path('admin/storage/edit/<int:storage_id>/', views.StorageUpdate.as_view(), name='storage_update'),
     path('admin/storage/delete/<int:storage_id>/', views.StorageDelete.as_view(), name='storage_delete'),
     path('admin/brand/', views.BrandList.as_view(), name='brand_list'),

     # Owner endpoint access
     path('owner/', views.OwnerDashboard.as_view(), name='owner_dashboard'),
     path('owner/report/sales/', views.SalesReportList.as_view(), name='sales_report_list'),
     path('owner/report/sales/<int:sales_id>/', views.SalesReportDetail.as_view(), name='sales_report_detail'),
     path('owner/report/restock/', views.RestockReportList.as_view(), name='restock_report_list'),
     path('owner/report/restock/<int:restock_id>/', views.RestockReportDetail.as_view(), name='restock_report_detail'),
     path('owner/report/service/', views.ServiceReportList.as_view(), name='service_report_list'),
     path('owner/report/service/<int:service_id>/', views.ServiceReportDetail.as_view(), name='service_report_detail'),
     path('owner/profile/<int:user_id>/', views.ProfileDetail.as_view(), name='profile_detail'),
     path('owner/profile/edit/<int:user_id>/', views.ProfileUpdate.as_view(), name='profile_update'),
     path('owner/log/', views.LogList.as_view(), name='log'),
     path('owner/admin/', views.AdminList.as_view(), name='admin_list'),
     path('owner/admin/add/', views.AdminAdd.as_view(), name='admin_add'),
     path('owner/admin/edit/<int:pk>/', views.AdminUpdate.as_view(), name='admin_update'),
     path('owner/admin/delete/<int:pk>/', views.AdminDelete.as_view(), name='admin_delete'),
]
