from django.urls import path
from si_mbe import views


urlpatterns = [
    path('', views.Home.as_view(), name='homepage')
]
