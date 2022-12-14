from rest_framework import serializers
from si_mbe.models import (Restock, Restock_detail, Sales, Sales_detail,
                           Sparepart, Supplier)


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


class SalesDetailPostSerializers(serializers.ModelSerializer):
    sales_detail_id = serializers.IntegerField(required=False)

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart_id', 'quantity', 'is_grosir']


class SalesPostSerializers(serializers.ModelSerializer):
    content = SalesDetailPostSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = ['sales_id', 'customer_name', 'customer_contact', 'is_paid_off', 'content']

    def create(self, validated_data):
        # get the nested objects list
        details = validated_data.pop('sales_detail_set')
        sales = Sales.objects.create(**validated_data)
        for details in details:
            try:
                details.pop('sales_detail_id')
            except Exception:
                pass
            Sales_detail.objects.create(sales_id=sales, **details)
        return sales

    def update(self, instance, validated_data):
        # get the nested objects list
        validated_details = validated_data.pop('sales_detail_set')

        # Assigning input (validated_data) to object (instance)
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.customer_contact = validated_data.get('customer_contact', instance.customer_contact)
        instance.is_paid_off = validated_data.get('is_paid_off', instance.is_paid_off)

        # get all nested objects related with this instance and make a dict(id, object)
        details_dict = dict((i.sales_detail_id, i) for i in instance.sales_detail_set.all())

        for validated_detail in validated_details:
            if 'sales_detail_id' in validated_detail:
                # if exists sales_detail_id remove from the dict and update
                detail = details_dict.pop(validated_detail['sales_detail_id'])

                # remove sales_detail_id from validated data as we don't require it.
                validated_detail.pop('sales_detail_id')

                # loop through the rest of keys in validated data to assign it to its respective field
                for key in validated_detail.keys():
                    setattr(detail, key, validated_detail[key])

                detail.save()
            else:
                Sales_detail.objects.create(sales_id=instance, **validated_detail)

        # delete remaining elements because they're not present in update call
        if len(details_dict) > 0:
            for detail in details_dict.values():
                detail.delete()
        return instance


class RestockDetailSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')

    class Meta:
        model = Restock_detail
        fields = ['restock_detail_id', 'sparepart', 'individual_price', 'quantity']


class RestockSerializers(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    content = RestockDetailSerializers(many=True, source='restock_detail_set')

    class Meta:
        model = Restock
        fields = ['restock_id', 'no_faktur', 'due_date', 'supplier', 'is_paid_off', 'content']


class RestockDetailPostSerializers(serializers.ModelSerializer):
    restock_detail_id = serializers.IntegerField(required=False)

    class Meta:
        model = Restock_detail
        fields = ['restock_detail_id', 'sparepart_id', 'individual_price', 'quantity']


class RestockPostSerializers(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%d-%m-%Y")
    content = RestockDetailPostSerializers(many=True, source='restock_detail_set')

    class Meta:
        model = Restock
        fields = ['restock_id', 'no_faktur', 'due_date', 'supplier_id', 'is_paid_off', 'content']

    def create(self, validated_data):
        # get the nested objects list
        details = validated_data.pop('restock_detail_set')
        restock = Restock.objects.create(**validated_data)
        for details in details:
            try:
                details.pop('restock_detail_id')
            except Exception:
                pass
            Restock_detail.objects.create(restock_id=restock, **details)
        return restock

    def update(self, instance, validated_data):
        # get the nested objects list
        validated_details = validated_data.pop('restock_detail_set')

        # Assigning input (validated_data) to object (instance)
        instance.no_faktur = validated_data.get('customer_name', instance.no_faktur)
        instance.due_date = validated_data.get('customer_contact', instance.due_date)
        instance.supplier_id = validated_data.get('customer_contact', instance.supplier_id)
        instance.is_paid_off = validated_data.get('is_paid_off', instance.is_paid_off)

        # get all nested objects related with this instance and make a dict(id, object)
        details_dict = dict((i.restock_detail_id, i) for i in instance.restock_detail_set.all())

        for validated_detail in validated_details:
            if 'restock_detail_id' in validated_detail:
                # if exists restock_detail_id remove from the dict and update
                detail = details_dict.pop(validated_detail['restock_detail_id'])

                # remove restock_detail_id from validated data as we don't require it.
                validated_detail.pop('restock_detail_id')

                # loop through the rest of keys in validated data to assign it to its respective field
                for key in validated_detail.keys():
                    setattr(detail, key, validated_detail[key])

                detail.save()
            else:
                Restock_detail.objects.create(restock_id=instance, **validated_detail)

        # delete remaining elements because they're not present in update call
        if len(details_dict) > 0:
            for detail in details_dict.values():
                detail.delete()
        return instance


class SupplierSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['supplier_id', 'name', 'address', 'contact_number', 'salesman_name', 'salesman_contact']


class SalesReportSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.extend_user.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'admin',
            'created_at',
            'updated_at',
            'customer_name',
            'customer_contact',
            'is_paid_off',
        ]


class SalesReportDetailSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.extend_user.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    content = SalesDetailSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'admin',
            'created_at',
            'updated_at',
            'customer_name',
            'customer_contact',
            'is_paid_off',
            'content',
        ]


class RestockReportSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.extend_user.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    supplier_contact = serializers.ReadOnlyField(source='supplier_id.contact_number')
    salesman = serializers.ReadOnlyField(source='supplier_id.salesman_name')
    salesman_contact = serializers.ReadOnlyField(source='supplier_id.salesman_contact')

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'admin',
            'created_at',
            'updated_at',
            'no_faktur',
            'is_paid_off',
            'due_date',
            'supplier',
            'supplier_contact',
            'salesman',
            'salesman_contact',
        ]
