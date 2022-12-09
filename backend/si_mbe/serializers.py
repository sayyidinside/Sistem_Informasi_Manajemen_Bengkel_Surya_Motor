from rest_framework import serializers
from si_mbe.models import Sales, Sales_detail, Sparepart


class SearchSparepartSerializers(serializers.ModelSerializer):
    """
    serializers for searching sparepart
    """
    brand_id = serializers.ReadOnlyField(source='brand_id.name')

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'name',
            'partnumber',
            'quantity',
            'motor_type',
            'sparepart_type',
            'brand_id',
            'price',
            'grosir_price',
        ]


class SparepartSerializers(serializers.ModelSerializer):
    """
    serializers for searching sparepart
    """
    brand_id = serializers.ReadOnlyField(source='brand_id.name')

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'name',
            'partnumber',
            'quantity',
            'motor_type',
            'sparepart_type',
            'brand_id',
            'price',
            'grosir_price',
            'created_at',
            'updated_at',
        ]


class SalesDetailSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart', 'quantity', 'is_grosir']


class SalesSerializers(serializers.ModelSerializer):
    content = SalesDetailSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = ['sales_id', 'customer_name', 'customer_contact', 'is_paid_off', 'content']
