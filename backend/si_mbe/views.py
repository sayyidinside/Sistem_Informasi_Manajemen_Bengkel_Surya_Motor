from django.http import Http404
from rest_framework import authentication, filters, generics, status
from rest_framework.response import Response
from si_mbe.exceptions import SparepartNotFound
from si_mbe.models import Sales, Sparepart
from si_mbe.paginations import CustomPagination
from si_mbe.permissions import IsAdminRole, IsLogin
from si_mbe.serializers import (SalesSerializers, SalesPostSerializers, SearchSparepartSerializers,
                                SparepartSerializers)


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


class Dashboard(generics.GenericAPIView):
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Berhasil mengkases dashboard'}, status=status.HTTP_200_OK)


class SparepartDataList(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('sparepart_id')
    serializer_class = SearchSparepartSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]


class SparepartDataAdd(generics.CreateAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, *args, **kwargs):
        if len(request.data) < 6:
            return Response({'message': 'Data sparepart tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data sparepart berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SparepartDataUpdate(generics.UpdateAPIView):
    queryset = Sparepart.objects.all()
    serializer_class = SparepartSerializers
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]
    lookup_field = 'sparepart_id'
    lookup_url_kwarg = 'sparepart_id'

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            exc = SparepartNotFound()
        return super().handle_exception(exc)

    def update(self, request, *args, **kwargs):
        if len(request.data) < 6:
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
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class SalesList(generics.ListAPIView):
    queryset = Sales.objects.all().order_by('sales_id')
    serializer_class = SalesSerializers
    pagination_class = CustomPagination
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]


class SalesAdd(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesPostSerializers
    permission_classes = [IsLogin, IsAdminRole]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, *args, **kwargs):
        # print(request.data)
        if len(request.data) < 4:
            return Response({'message': 'Data sparepart tidak sesuai / tidak lengkap'},
                            status=status.HTTP_400_BAD_REQUEST)
        for content in request.data['content']:
            if len(content) < 3:
                return Response({'message': 'Data sparepart tidak sesuai / tidak lengkap'},
                                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['message'] = 'Data penjualan berhasil ditambah'
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
