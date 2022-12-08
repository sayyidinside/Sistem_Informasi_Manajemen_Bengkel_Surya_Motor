from django.urls import path
from si_mbe import views


urlpatterns = [
    path('', views.Home.as_view(), name='homepage'),
    path('sparepart/find/', views.SearchSparepart.as_view(), name='search_sparepart'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/sparepart/', views.SparepartDataList.as_view(), name='sparepart_data_list'),
    path('dashboard/sparepart/add/', views.SparepartDataAdd.as_view(), name='sparepart_data_add'),
    path('dahsboard/sparepart/edit/<int:sparepart_id>', views.SparepartDataUpdate.as_view(),
         name='sparepart_data_update')
]
