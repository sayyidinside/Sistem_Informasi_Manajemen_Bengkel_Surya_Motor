# from django.shortcuts import render
from rest_framework import filters, generics, status, authentication
from rest_framework.response import Response
from si_mbe.models import Sparepart
from si_mbe.paginations import CustomPagination
from si_mbe.serializers import SearchSparepartSerializers, SparepartSerializers
from si_mbe.permissions import IsLogin, IsAdminRole


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
