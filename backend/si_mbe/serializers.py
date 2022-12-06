from rest_framework import serializers
from si_mbe.models import Sparepart


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
            'price',
            'grosir_price',
            'brand_id'
        ]
