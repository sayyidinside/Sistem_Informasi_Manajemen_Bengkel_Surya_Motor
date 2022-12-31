from calendar import monthrange
from datetime import date, timedelta

from dj_rest_auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.http import Http404
from rest_framework import filters, generics, status
from rest_framework.response import Response
from si_mbe import exceptions, serializers
from si_mbe.models import (Brand, Category, Customer, Logs, Mechanic, Profile,
                           Restock, Sales, Salesman, Service, Sparepart,
                           Storage, Supplier)
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
    queryset = Restock.objects.prefetch_related('restock_detail_set').filter(
        Q(due_date__range=(date.today(), date.today() + timedelta(days=7))) &
        Q(is_paid_off=False)
        ).order_by('due_date')
    permission_classes = [IsLogin, IsAdminRole]
    serializer_class = serializers.RestockDueSerializers

    def get(self, request, *args, **kwargs):
        # Getting restock due data
        restock_due_queryset = self.filter_queryset(self.get_queryset())
        restock_due = self.get_serializer(restock_due_queryset, many=True)

        # Getting sparepart on limit data
        self.queryset = Sparepart.objects.select_related('brand_id').filter(
            Q(quantity__lte=F('limit'))
        ).order_by('quantity')
        self.serializer_class = serializers.SparepartOnLimitSerializers
        sparepart_on_limit_queryset = self.filter_queryset(self.get_queryset())
        sparepart_on_limit = self.get_serializer(sparepart_on_limit_queryset, many=True)

        # Getting 10 most sold sparepart in a month
        self.queryset = Sparepart.objects.prefetch_related('sales_detail_set', 'service_sparepart_set')
        self.serializer_class = serializers.SparepartMostSoldSerializers
        most_sold_queryset = self.filter_queryset(self.get_queryset())
        most_sold = self.get_serializer(most_sold_queryset, many=True)
        most_sold = sorted(most_sold.data, key=lambda k: k['total_sold'], reverse=True)

        # Getting 10 most used sparepart from services in a month
        self.serializer_class = serializers.SparepartMostUsedSerializers
        most_used_queryset = self.filter_queryset(self.get_queryset())
        most_used = self.get_serializer(most_used_queryset, many=True)
        most_used = sorted(most_used.data, key=lambda k: k['total_used'], reverse=True)

        return Response({
            'sparepart_on_limit': sparepart_on_limit.data,
            'restock_due': restock_due.data,
            'most_sold': most_sold[:10],
            'most_used': most_used[:10]
            },
            status=status.HTTP_200_OK
        )


class SparepartDataList(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('sparepart_id')
    serializer_class = serializers.SparepartListSerializers
    permission_classes = [IsLogin, IsAdminRole]

    pagination_class = CustomPagination
    pagination_class.page_size = 100

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'partnumber', 'brand_id__name', 'category_id__name']

    def get_paginated_response(self, data):
        if len(data) == 0:
            self.pagination_class.message = 'Sparepart yang dicari tidak ditemukan'
            self.pagination_class.status = status.HTTP_200_OK
        return super().get_paginated_response(data)


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
    queryset = Sales.objects.all().order_by('sales_id')
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

    def perform_create(self, serializer):
        # Save the new Sales instance to the database
        instance = serializer.save()

        # Subtracting spareapart quantity with new sales detail data
        for sales_detail in instance.sales_detail_set.all():
            # Get the Sparepart instance associated with the Sales_detail instance
            sparepart = sales_detail.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= sales_detail.quantity
            sparepart.save()


class SalesUpdate(generics.RetrieveUpdateAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
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

    def perform_update(self, serializer):
        # Get the old Sales instance and its associated Sales_detail instances
        old_instance = self.get_object()
        old_sales_details = old_instance.sales_detail_set.all().order_by('sales_detail_id')

        # Getting list of dict from old data, for post save calculaltion
        old_data_list = []
        for old_data in old_sales_details:
            old_data_list.append(
                {
                    'sales_detail_id': old_data.sales_detail_id,
                    'quantity': old_data.quantity,
                    'sparepart_id': old_data.sparepart_id
                }
            )

        # Update the Sales instance in the database
        instance = serializer.save()

        # Adding (plus) Sparepart quantity with old sales detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Sales_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance

            sparepart.quantity += old_data['quantity']
            sparepart.save()

        # Subtracting spareapart quantity with new sales detail data
        for sales_detail in instance.sales_detail_set.all():
            # Get the Sparepart instance associated with the new Sales_detail instance
            sparepart = sales_detail.sparepart_id

            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= sales_detail.quantity
            sparepart.save()


class SalesDelete(generics.DestroyAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
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

    def perform_destroy(self, instance):
        # Get the old Sales instance and its associated Sales_detail instances
        old_instance = self.get_object()
        old_sales_details = old_instance.sales_detail_set.all().order_by('sales_detail_id')

        # Getting list of dict from old data, for post save calculaltion
        old_data_list = []
        for old_data in old_sales_details:
            old_data_list.append(
                {
                    'sales_detail_id': old_data.sales_detail_id,
                    'quantity': old_data.quantity,
                    'sparepart_id': old_data.sparepart_id
                }
            )

        # Deleting instance in database
        instance.delete()

        # Adding (plus) Sparepart quantity with old sales detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Sales_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += old_data['quantity']
            sparepart.save()


class RestockList(generics.ListAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
    serializer_class = serializers.RestockSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]


class RestockAdd(generics.CreateAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
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

    def perform_create(self, serializer):
        # Save the new Restock instance to the database
        instance = serializer.save()

        # Subtracting spareapart quantity with new restock detail data
        for restock_detail in instance.restock_detail_set.all():
            # Get the Sparepart instance associated with the Restock_detail instance
            sparepart = restock_detail.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += restock_detail.quantity
            sparepart.save()


class RestockUpdate(generics.RetrieveUpdateAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
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

    def perform_update(self, serializer):
        # Get the old Restock instance and its associated Restock_detail instances
        old_instance = self.get_object()
        old_restock_details = old_instance.restock_detail_set.all().order_by('restock_detail_id')

        # Getting list of dict from old data, for post save calculaltion
        old_data_list = []
        for old_data in old_restock_details:
            old_data_list.append(
                {
                    'restock_detail_id': old_data.restock_detail_id,
                    'quantity': old_data.quantity,
                    'sparepart_id': old_data.sparepart_id
                }
            )

        # Update the Sales instance in the database
        instance = serializer.save()

        # Subtracting Sparepart quantity with old restock detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Restock_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= old_data['quantity']
            sparepart.save()

        # Adding (+) spareapart quantity with new restock detail data
        for sales_detail in instance.restock_detail_set.all():
            # Get the Sparepart instance associated with the new Restock_detail instance
            sparepart = sales_detail.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += sales_detail.quantity
            sparepart.save()


class RestockDelete(generics.DestroyAPIView):
    queryset = Restock.objects.all().order_by('restock_id')
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

    def perform_destroy(self, instance):
        # Get the old Restock instance and its associated Restock_detail instances
        old_instance = self.get_object()
        old_restock_details = old_instance.restock_detail_set.all().order_by('restock_detail_id')

        # Getting list of dict from old data, for post save calculaltion
        old_data_list = []
        for old_data in old_restock_details:
            old_data_list.append(
                {
                    'restock_detail_id': old_data.restock_detail_id,
                    'quantity': old_data.quantity,
                    'sparepart_id': old_data.sparepart_id
                }
            )

        # Deleting instance in database
        instance.delete()

        # Adding (plus) Sparepart quantity with old restock detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Restock_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= old_data['quantity']
            sparepart.save()


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
        # Getting url params of year and month if doesn't exist use today value
        self.year = int(request.query_params.get('year', date.today().year))
        self.month = int(request.query_params.get('month', date.today().month))

        # Getting number of day form current month
        self.number_of_day = monthrange(year=self.year, month=self.month)[1]

        # Getting total revenue per day in particular a month
        self.revenue_in_month = {}

        # Getting sparepart revenue for today
        self.sales_revenue_today = 0

        # Getting service revenue for today
        self.service_revenue_today = 0

        # Getting total revenue for today
        self.total_revenue_today = 0

        # Getting revenue from sales
        self.queryset = Sales.objects.prefetch_related('sales_detail_set')
        self.serializer_class = serializers.SalesRevenueSerializers
        sales_queryset = self.filter_queryset(self.get_queryset())
        sales = self.get_serializer(sales_queryset, many=True)
        sales_list = sorted(sales.data, key=lambda k: k['created_at'], reverse=True)

        # Getting revenue from service
        self.queryset = Service.objects.prefetch_related('service_sparepart_set', 'service_action_set')
        self.serializer_class = serializers.ServiceRevenueSerializers
        service_queryset = self.filter_queryset(self.get_queryset())
        service = self.get_serializer(service_queryset, many=True)
        service_list = sorted(service.data, key=lambda k: k['created_at'], reverse=True)

        # Make dict of revenue per day in particular month as exp {day: revenue_total}
        for i, object in enumerate(range(self.number_of_day), 1):
            self.revenue_in_month[i] = 0
            for sales in sales_list:
                if sales['created_at'] == date(self.year, self.month, i).strftime('%d-%m-%Y'):
                    self.revenue_in_month[i] += sales['revenue']
                    if date(self.year, self.month, i).strftime('%d-%m-%Y') == date.today().strftime('%d-%m-%Y'):
                        self.sales_revenue_today += sales['revenue']
                        self.total_revenue_today += sales['revenue']
            for service in service_list:
                if service['created_at'] == date(self.year, self.month, i).strftime('%d-%m-%Y'):
                    self.revenue_in_month[i] += service['revenue']
                    if date(self.year, self.month, i).strftime('%d-%m-%Y') == date.today().strftime('%d-%m-%Y'):
                        self.service_revenue_today += service['revenue']
                        self.total_revenue_today += service['revenue']

        # Getting number of sales from today
        self.count_sales = Sales.objects.filter(created_at__date=date.today()).count()

        # Getting number of service from today
        self.count_service = Service.objects.filter(created_at__date=date.today()).count()

        # Getting expenditure total from today
        self.expenditure_today = 0

        self.queryset = Restock.objects.prefetch_related('restock_detail_set')
        self.serializer_class = serializers.RestockExpenditureSerializers

        restock_queryset = self.filter_queryset(self.get_queryset())
        restock = self.get_serializer(restock_queryset, many=True)
        restock_list = sorted(restock.data, key=lambda k: k['created_at'], reverse=True)

        for restock in restock_list:
            if restock['created_at'] == date.today().strftime('%d-%m-%Y'):
                self.expenditure_today += restock['expenditure']

        return Response(
            {
                'message': 'Berhasil Mengkases Pemilik Dashboard',
                'revenue_in_month': self.revenue_in_month,
                'sales_revenue_today': self.sales_revenue_today,
                'service_revenue_today': self.service_revenue_today,
                'total_revenue_today': self.total_revenue_today,
                'sales_count_today': self.count_sales,
                'service_count_today': self.count_service,
                'expenditure_today': self.expenditure_today
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
    queryset = Service.objects.prefetch_related(
        'service_action_set', 'service_sparepart_set'
    ).order_by('service_id')

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

    def perform_create(self, serializer):
        # Save the new Service instance to the database
        instance = serializer.save()

        # Subtracting spareapart quantity with new service_sparepart data
        for service_sparepart in instance.service_sparepart_set.all():
            # Get the Sparepart instance associated with the Service_sparepart instance
            sparepart = service_sparepart.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= service_sparepart.quantity
            sparepart.save()


class ServiceUpdate(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.prefetch_related(
        'service_action_set', 'service_sparepart_set'
    ).order_by('service_id')
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

    def perform_update(self, serializer):
        # Get the old Service instance and its associated Service_sparepart instances
        old_instance = self.get_object()
        old_service_spareparts = old_instance.service_sparepart_set.all()

        # Save intance to database
        instance = serializer.save()

        # looping trought new service sparepart data to adjust sparepart quantity
        for service_sparepart in instance.service_sparepart_set.all():
            # Get the Sparepart instance associated with the Service_sparepart instance
            sparepart = service_sparepart.sparepart_id

            # Find the old Service_sparepart instance with the same sparepart_id
            old_service_sparepart = next(
                (ss for ss in old_service_spareparts if ss.sparepart_id == sparepart),
                None
            )

            # Update the quantity field of the Sparepart instance:
            # 1. If an old Service_action instance was found, increase the quantity field of
            # the Sparepart instance by the old quantity value
            if old_service_sparepart:
                sparepart.quantity += old_service_sparepart.quantity

            # 2. Decrease the quantity field of the Sparepart instance by the new quantity value
            sparepart.quantity -= service_sparepart.quantity
            sparepart.save()

        # Loop over all the old Service_sparepart instances
        for old_service_sparepart in old_service_spareparts:
            # Check if the old Service_sparepart instance is not present in the
            # new data / updated instance
            if old_service_sparepart not in instance.service_sparepart_set.all():
                sparepart = old_service_sparepart.sparepart_id
                # increase the quantity field of the Sparepart instance by the old
                # quantity value
                sparepart.quantity += old_service_sparepart.quantity
                sparepart.save()


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

    def perform_destroy(self, instance):
        # Get the old Sales instance and its associated service_sparepart instances
        old_instance = self.get_object()
        old_service_spareparts = old_instance.service_sparepart_set.all().order_by('service_sparepart_id')

        # Getting list of dict from old data, for post save calculaltion
        old_data_list = []
        for old_data in old_service_spareparts:
            old_data_list.append(
                {
                    'service_sparepart_id': old_data.service_sparepart_id,
                    'quantity': old_data.quantity,
                    'sparepart_id': old_data.sparepart_id
                }
            )

        # Deleting instance in database
        instance.delete()

        # Adding (plus) Sparepart quantity with old service_sparepart data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old service_sparepart instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += old_data['quantity']
            sparepart.save()


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
