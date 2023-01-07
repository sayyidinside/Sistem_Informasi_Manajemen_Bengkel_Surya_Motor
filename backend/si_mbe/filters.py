from django_filters import rest_framework as filter
from si_mbe.models import Sparepart, Brand, Category


class SparepartFilter(filter.FilterSet):
    name = filter.CharFilter(
        lookup_expr='icontains',
        field_name='name',
        label='Sparepart Name'
    )
    brand = filter.ModelChoiceFilter(
        queryset=Brand.objects.all(),
        lookup_expr='exact',
        field_name='brand_id',
        label='Brand'
    )
    category = filter.ModelChoiceFilter(
        queryset=Category.objects.all(),
        lookup_expr='exact',
        field_name='category_id',
        label='Category'
    )
    motor_type = filter.CharFilter(
        lookup_expr='icontains',
        field_name='motor_type',
        label='Motor Type'
    )

    class Meta:
        model = Sparepart
        fields = ['name', 'brand', 'category', 'motor_type']
