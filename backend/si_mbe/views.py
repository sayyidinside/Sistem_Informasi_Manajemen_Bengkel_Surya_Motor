from calendar import monthrange
from datetime import date

from dj_rest_auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import filters, generics, status
from rest_framework.response import Response
from si_mbe.exceptions import (AdminNotFound, RestockNotFound, SalesNotFound,
                               ServiceNotFound, SparepartNotFound,
                               StorageNotFound, SupplierNotFound)
from si_mbe.models import (Logs, Profile, Restock, Sales, Service, Sparepart,
                           Storage, Supplier)
from si_mbe.paginations import CustomPagination
from si_mbe.permissions import (IsAdminRole, IsLogin, IsOwnerRole,
                                IsRelatedUserOrAdmin)
from si_mbe.serializers import (AdminPostSerializers, AdminSerializers,
                                AdminUpdateSerializers, LogSerializers,
                                ProfileSerializers, ProfileUpdateSerializers,
                                RestockPostSerializers,
                                RestockReportDetailSerializers,
                                RestockReportSerializers, RestockSerializers,
                                SalesPostSerializers,
                                SalesReportDetailSerializers,
                                SalesReportSerializers, SalesSerializers,
                                SearchSparepartSerializers,
                                ServicePostSerializers,
                                ServiceReportDetailSerializers,
                                ServiceReportSerializers, ServiceSerializers,
                                SparepartSerializers, StorageSerializers,
                                SupplierSerializers)
from si_mbe.utility import perform_log


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class SearchSparepart(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('name')
    serializer_class = SearchSparepartSerializers
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
    serializer_class = SearchSparepartSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SparepartDataAdd(generics.CreateAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = SparepartSerializers
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
    serializer_class = SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sparepart_id'
    lookup_url_kwarg = 'sparepart_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SparepartNotFound()
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
    serializer_class = SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]
    lookup_field = 'sparepart_id'
    lookup_url_kwarg = 'sparepart_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SparepartNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data sparepart berhasil dihapus'}

        perform_log(request=request, operation='R', table='Sparepart')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesList(generics.ListAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
    serializer_class = SalesSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SalesAdd(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesPostSerializers
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
    serializer_class = SalesPostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SalesNotFound()
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
    serializer_class = SalesPostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SalesNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data penjualan berhasil dihapus'}

        perform_log(request=request, operation='R', table='Sales')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class RestockList(generics.ListAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
    serializer_class = RestockSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class RestockAdd(generics.CreateAPIView):
    queryset = Restock.objects.all()
    serializer_class = RestockPostSerializers
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
    serializer_class = RestockPostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = RestockNotFound()
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
    serializer_class = RestockPostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = RestockNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data pengadaan berhasil dihapus'}

        perform_log(request=request, operation='R', table='Restock')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SupplierList(generics.ListAPIView):
    queryset = Supplier.objects.all().order_by('supplier_id')
    serializer_class = SupplierSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class SupplierAdd(generics.CreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializers
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
    serializer_class = SupplierSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'supplier_id'
    lookup_url_kwarg = 'supplier_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SupplierNotFound()
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
    serializer_class = SupplierSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'supplier_id'
    lookup_url_kwarg = 'supplier_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SupplierNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data supplier berhasil dihapus'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesReportList(generics.ListAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
    serializer_class = SalesReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class SalesReportDetail(generics.RetrieveAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'sales_id'
    lookup_url_kwarg = 'sales_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SalesNotFound()
        return super().handle_exception(exc)


class RestockReportList(generics.ListAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
    serializer_class = RestockReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class RestockReportDetail(generics.RetrieveAPIView):
    queryset = Restock.objects.all()
    serializer_class = RestockReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'restock_id'
    lookup_url_kwarg = 'restock_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = RestockNotFound()
        return super().handle_exception(exc)


class CustomPasswordChangeView(PasswordChangeView):
    permission_classes = [IsLogin]


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializers
    permission_classes = [IsLogin, IsRelatedUserOrAdmin]

    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'


class ProfileUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializers
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
    serializer_class = LogSerializers
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
    serializer_class = AdminSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class AdminAdd(generics.CreateAPIView):
    queryset = User.objects.prefetch_related('profile').filter(profile__role='A', is_active=True)
    serializer_class = AdminPostSerializers
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
    serializer_class = AdminUpdateSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = AdminNotFound()
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
    serializer_class = AdminPostSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = AdminNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()

        message = {'message': 'Data admin berhasil dihapus'}

        return Response(data=message, status=status.HTTP_204_NO_CONTENT)


class ServiceReportList(generics.ListAPIView):
    queryset = Service.objects.all().order_by('service_id')
    serializer_class = ServiceReportSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsOwnerRole]


class ServiceReportDetail(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceReportDetailSerializers
    permission_classes = [IsLogin, IsOwnerRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = ServiceNotFound()
        return super().handle_exception(exc)


class ServiceList(generics.ListAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set').order_by('service_id')
    serializer_class = ServiceSerializers
    permission_classes = [IsLogin, IsAdminRole]
    pagination_class = CustomPagination
    pagination_class.page_size = 100


class ServiceAdd(generics.CreateAPIView):
    queryset = Service.objects.prefetch_related('service_action_set', 'service_sparepart_set')
    serializer_class = ServicePostSerializers
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
    serializer_class = ServicePostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = ServiceNotFound()
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
    serializer_class = ServicePostSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'service_id'
    lookup_url_kwarg = 'service_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = ServiceNotFound()
        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = {'message': 'Data servis berhasil dihapus'}

        perform_log(request=request, operation='R', table='Service')

        return Response(message, status=status.HTTP_204_NO_CONTENT)


class StorageList(generics.ListAPIView):
    queryset = Storage.objects.all().order_by('storage_id')
    serializer_class = StorageSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class StorageAdd(generics.CreateAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializers
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
    serializer_class = StorageSerializers
    permission_classes = [IsLogin, IsAdminRole]

    lookup_field = 'storage_id'
    lookup_url_kwarg = 'storage_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = StorageNotFound()
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
