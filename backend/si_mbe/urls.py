from django.urls import path
from si_mbe import views


urlpatterns = [
    path('', views.Home.as_view(), name='homepage'),
    path('sparepart/find/', views.SearchSparepart.as_view(), name='search_sparepart'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
]
