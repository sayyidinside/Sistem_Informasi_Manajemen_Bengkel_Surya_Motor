from calendar import monthrange
from datetime import date

from dj_rest_auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import filters, generics, status
from rest_framework.response import Response
from si_mbe import exceptions, serializers
from si_mbe.models import (Brand, Category, Customer, Logs, Mechanic, Profile,
                           Restock, Sales, Service, Sparepart, Storage,
                           Supplier, Salesman)
from si_mbe.paginations import CustomPagination
from si_mbe.permissions import (IsAdminRole, IsLogin, IsOwnerRole,
                                IsRelatedUserOrAdmin)
from si_mbe.utility import perform_log


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class SearchSparepart(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('name')
    serializer_class = serializers.SearchSparepartSerializers
    pagination_class = CustomPagination

    lookup_field = 'sparepart_id'

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'partnumber', 'motor_type', 'sparepart_type', 'brand_id__name']

    def get_paginated_response(self, data):
        if len(data) == 0:
            self.pagination_class.message = 'Sparepart yang dicari tidak ditemukan'
            self.pagination_class.status = status.HTTP_200_OK
        else:
            self.pagination_class.message = 'Pencarian sparepart berhasil'
            self.pagination_class.status = status.HTTP_200_OK
        return super().get_paginated_response(data)


class AdminDashboard(generics.GenericAPIView):
    permission_classes = [IsLogin, IsAdminRole]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Berhasil mengkases admin dashboard'}, status=status.HTTP_200_OK)


class SparepartDataList(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('sparepart_id')
    serializer_class = serializers.SearchSparepartSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SparepartDataAdd(generics.CreateAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = serializers.SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 10:
            return Response({'message': 'Data sparepart tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data sparepart berhasil ditambah'

        perform_log(request=request, operation='C', table='Sparepart')

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SparepartDataUpdate(generics.RetrieveUpdateAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = serializers.SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sparepart_id'
    lookup_url_kwarg = 'sparepart_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SparepartNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 10:
            return Response({'message': 'Data sparepart tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data sparepart berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        perform_log(request=request, operation='E', table='Sparepart')

        return Response(data)


class SparepartDataDelete(generics.DestroyAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = serializers.SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]
    lookup_field = 'sparepart_id'
    lookup_url_kwarg = 'sparepart_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SparepartNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data sparepart berhasil dihapus'}

        perform_log(request=request, operation='R', table='Sparepart')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesList(generics.ListAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
    serializer_class = serializers.SalesSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SalesAdd(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = serializers.SalesManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 4:
            return Response({'message': 'Data penjualan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for content in request.data['content']:
            if len(content) < 3:
                return Response({'message': 'Data penjualan tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data penjualan berhasil ditambah'

        perform_log(request=request, operation='C', table='Sales')

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SalesUpdate(generics.RetrieveUpdateAPIView):
    queryset = Sales.objects.all()
    serializer_class = serializers.SalesManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SalesNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 4:
            return Response({'message': 'Data penjualan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for content in request.data['content']:
            if len(content) < 4:
                return Response({'message': 'Data penjualan tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data penjualan berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        perform_log(request=request, operation='E', table='Sales')

        return Response(data)


class SalesDelete(generics.DestroyAPIView):
    queryset = Sales.objects.all()
    serializer_class = serializers.SalesManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SalesNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data penjualan berhasil dihapus'}

        perform_log(request=request, operation='R', table='Sales')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class RestockList(generics.ListAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
    serializer_class = serializers.RestockSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class RestockAdd(generics.CreateAPIView):
    queryset = Restock.objects.all()
    serializer_class = serializers.RestockManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 7:
            return Response({'message': 'Data pengadaan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for content in request.data['content']:
            if len(content) < 3:
                return Response({'message': 'Data pengadaan tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data pengadaan berhasil ditambah'

        perform_log(request=request, operation='C', table='Restock')

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class RestockUpdate(generics.RetrieveUpdateAPIView):
    queryset = Restock.objects.all()
    serializer_class = serializers.RestockManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.RestockNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 7:
            return Response({'message': 'Data pengadaan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for content in request.data['content']:
            if len(content) < 4:
                return Response({'message': 'Data pengadaan tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data pengadaan berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        perform_log(request=request, operation='E', table='Restock')

        return Response(data)


class RestockDelete(generics.DestroyAPIView):
    queryset = Restock.objects.all()
    serializer_class = serializers.RestockManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.RestockNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data pengadaan berhasil dihapus'}

        perform_log(request=request, operation='R', table='Restock')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SupplierList(generics.ListAPIView):
    queryset = Supplier.objects.all().order_by('supplier_id')
    serializer_class = serializers.SupplierSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SupplierAdd(generics.CreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data supplier tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data supplier berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SupplierUpdate(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'supplier_id'
    lookup_url_kwarg = 'supplier_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SupplierNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data supplier tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data supplier berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class SupplierDelete(generics.DestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'supplier_id'
    lookup_url_kwarg = 'supplier_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SupplierNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data supplier berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesReportList(generics.ListAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
    serializer_class = serializers.SalesReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class SalesReportDetail(generics.RetrieveAPIView):
    queryset = Sales.objects.all()
    serializer_class = serializers.SalesReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SalesNotFound()
        return super().handle_exception(exc)


class RestockReportList(generics.ListAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
    serializer_class = serializers.RestockReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class RestockReportDetail(generics.RetrieveAPIView):
    queryset = Restock.objects.all()
    serializer_class = serializers.RestockReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.RestockNotFound()
        return super().handle_exception(exc)


class CustomPasswordChangeView(PasswordChangeView):
    permission_classes = [IsLogin]


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializers
    permission_classes = [IsLogin, IsRelatedUserOrAdmin]

    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'


class ProfileUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileUpdateSerializers
    permission_classes = [IsLogin, IsRelatedUserOrAdmin]

    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data profile tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Profile berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class LogList(generics.ListAPIView):
    queryset = Logs.objects.all().order_by('log_id')
    serializer_class = serializers.LogSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class OwnerDashboard(generics.GenericAPIView):
    permission_classes = [IsLogin, IsOwnerRole]

    def get(self, request, *args, **kwargs):
        # Getting number of day form current month
        self.number_of_day = monthrange(date.today().year, date.today().month)[1]

        # Create dict to store number of sales per day in current month
        self.sales_in_month = {}
        for i, object in enumerate(range(self.number_of_day), 1):
            self.sales_in_month[i] = len(Sales.objects.filter(created_at__date=date(
                                        year=date.today().year,
                                        month=date.today().month,
                                        day=i
                                    )))

        # Getting number of sales from today
        self.count_sales = len(Sales.objects.filter(created_at__date=date.today()))
        return Response(
            {
                'message': 'Berhasil Mengkases Pemilik Dashboard',
                'sales_today': self.count_sales,
                'sales_in_mont': self.sales_in_month
            },
            status=status.HTTP_200_OK)


class AdminList(generics.ListAPIView):
    queryset = User.objects.prefetch_related('profile').filter(is_active=True, profile__role='A').order_by('id')
    serializer_class = serializers.AdminSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class AdminAdd(generics.CreateAPIView):
    queryset = User.objects.prefetch_related('profile').filter(profile__role='A', is_active=True)
    serializer_class = serializers.AdminManagementSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    def create(self, request, *args, **kwargs):
        # Check if user give incomplete input
        if len(request.data) < 7:
            return Response({'message': 'Data admin tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if password and confirm passowrd is different
        if self.request.data['password'] != self.request.data['password_2']:
            return Response({'message': 'Password dan Konfirmasi Password Berbeda'},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class AdminUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.prefetch_related('profile').filter(profile__role='A', is_active=True)
    serializer_class = serializers.AdminUpdateSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.AdminNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 5:
            return Response({'message': 'Data admin tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Admin berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class AdminDelete(generics.DestroyAPIView):
    queryset = User.objects.prefetch_related('profile').filter(profile__role='A', is_active=True)
    serializer_class = serializers.AdminManagementSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.AdminNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()

        message = {'message': 'Data admin berhasil dihapus'}

        return Response(data=message, status=status.HTTP_204_NO_CONTENT)


class ServiceReportList(generics.ListAPIView):
    queryset = Service.objects.all().order_by('service_id')
    serializer_class = serializers.ServiceReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class ServiceReportDetail(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = serializers.ServiceReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.ServiceNotFound()
        return super().handle_exception(exc)


class ServiceList(generics.ListAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set').order_by('service_id')
    serializer_class = serializers.ServiceSerializers
    permission_classes = [IsLogin, IsAdminRole]
    pagination_class = CustomPagination
    pagination_class.page_size = 100


class ServiceAdd(generics.CreateAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set')
    serializer_class = serializers.ServiceManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 9:
            return Response({'message': 'Data servis tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data servis berhasil ditambah'

        perform_log(request=request, operation='C', table='Service')

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class ServiceUpdate(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set')
    serializer_class = serializers.ServiceManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.ServiceNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 9:
            return Response({'message': 'Data servis tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for action in request.data['service_actions']:
            if len(action) < 3:
                return Response({'message': 'Data servis tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)
        for sparepart in request.data['service_spareparts']:
            if len(sparepart) < 3:
                return Response({'message': 'Data servis tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data servis berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        perform_log(request=request, operation='E', table='Service')

        return Response(data)


class ServiceDelete(generics.DestroyAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set')
    serializer_class = serializers.ServiceManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.ServiceNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data servis berhasil dihapus'}

        perform_log(request=request, operation='R', table='Service')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class StorageList(generics.ListAPIView):
    queryset = Storage.objects.all().order_by('storage_id')
    serializer_class = serializers.StorageSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class StorageAdd(generics.CreateAPIView):
    queryset = Storage.objects.all()
    serializer_class = serializers.StorageSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data lokasi penyimpanan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data lokasi penyimpanan berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class StorageUpdate(generics.RetrieveUpdateAPIView):
    queryset = Storage.objects.all()
    serializer_class = serializers.StorageSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'storage_id'
    lookup_url_kwarg = 'storage_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.StorageNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data lokasi penyimpanan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data lokasi penyimpanan berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class StorageDelete(generics.DestroyAPIView):
    queryset = Storage.objects.all()
    serializer_class = serializers.StorageSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'storage_id'
    lookup_url_kwarg = 'storage_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.StorageNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data lokasi penyimpanan berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class BrandList(generics.ListAPIView):
    queryset = Brand.objects.all().order_by('brand_id')
    serializer_class = serializers.BrandSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class BrandAdd(generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = serializers.BrandSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 1:
            return Response({'message': 'Data merek / brand tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data merek / brand berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BrandUpdate(generics.RetrieveUpdateAPIView):
    queryset = Brand.objects.all()
    serializer_class = serializers.BrandSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'brand_id'
    lookup_url_kwarg = 'brand_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.BrandNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 1:
            return Response({'message': 'Data merek / brand tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data merek / brand berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class BrandDelete(generics.DestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = serializers.BrandSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'brand_id'
    lookup_url_kwarg = 'brand_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.BrandNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data merek / brand berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all().order_by('category_id')
    serializer_class = serializers.CategorySerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class CategoryAdd(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 1:
            return Response({'message': 'Data kategori tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data kategori berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CategoryUpdate(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'category_id'
    lookup_url_kwarg = 'category_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.CategoryNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 1:
            return Response({'message': 'Data kategori tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data kategori berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class CategoryDelete(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'category_id'
    lookup_url_kwarg = 'category_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.CategoryNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data kategori berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all().order_by('customer_id')
    serializer_class = serializers.CustomerSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class CustomerAdd(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 4:
            return Response({'message': 'Data pelanggan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data pelanggan berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CustomerUpdate(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'customer_id'
    lookup_url_kwarg = 'customer_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.CustomerNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 4:
            return Response({'message': 'Data pelanggan tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data pelanggan berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class CustomerDelete(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'customer_id'
    lookup_url_kwarg = 'customer_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.CustomerNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data pelanggan berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class MechanicList(generics.ListAPIView):
    queryset = Mechanic.objects.all().order_by('mechanic_id')
    serializer_class = serializers.MechanicSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class MechanicAdd(generics.CreateAPIView):
    queryset = Mechanic.objects.all()
    serializer_class = serializers.MechanicSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data mekanik tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data mekanik berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class MechanicUpdate(generics.RetrieveUpdateAPIView):
    queryset = Mechanic.objects.all()
    serializer_class = serializers.MechanicSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'mechanic_id'
    lookup_url_kwarg = 'mechanic_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.MechanicNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data mekanik tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data mekanik berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class MechanicDelete(generics.DestroyAPIView):
    queryset = Mechanic.objects.all()
    serializer_class = serializers.MechanicSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'mechanic_id'
    lookup_url_kwarg = 'mechanic_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.MechanicNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data mekanik berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesmanList(generics.ListAPIView):
    queryset = Salesman.objects.select_related('supplier_id').order_by('salesman_id')
    serializer_class = serializers.SalesmanSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SalesmanAdd(generics.CreateAPIView):
    queryset = Salesman.objects.select_related('supplier_id')
    serializer_class = serializers.SalesmanManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data salesman tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data salesman berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SalesmanUpdate(generics.RetrieveUpdateAPIView):
    queryset = Salesman.objects.select_related('supplier_id')
    serializer_class = serializers.SalesmanManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'salesman_id'
    lookup_url_kwarg = 'salesman_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SalesmanNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 3:
            return Response({'message': 'Data salesman tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['message'] = 'Data salesman berhasil dirubah'

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class SalesmanDelete(generics.DestroyAPIView):
    queryset = Salesman.objects.select_related('supplier_id')
    serializer_class = serializers.SalesmanManagementSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'salesman_id'
    lookup_url_kwarg = 'salesman_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = exceptions.SalesmanNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data salesman berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)
