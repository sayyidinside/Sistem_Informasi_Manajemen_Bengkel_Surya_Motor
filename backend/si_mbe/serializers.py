from datetime import date
from django.contrib.auth.models import User
from rest_framework import serializers
from si_mbe.models import (Brand, Category, Customer, Logs, Profile, Restock,
                           Restock_detail, Sales, Sales_detail, Service,
                           Service_action, Service_sparepart, Sparepart,
                           Storage, Supplier, Mechanic, Salesman)
from si_mbe.validators import validate_image_size
from django.core.validators import FileExtensionValidator


class SearchSparepartSerializers(serializers.ModelSerializer):
    """
    serializers for searching sparepart
    """
    brand = serializers.ReadOnlyField(source='brand_id.name')
    location = serializers.ReadOnlyField(source='storage_id.code')
    category = serializers.ReadOnlyField(source='category_id.name')
    image = serializers.ImageField(required=False, allow_empty_file=True, use_url=True)

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'image',
            'name',
            'partnumber',
            'quantity',
            'category',
            'motor_type',
            'sparepart_type',
            'brand',
            'price',
            'workshop_price',
            'install_price',
            'location',
        ]


class SparepartListSerializers(serializers.ModelSerializer):
    brand = serializers.ReadOnlyField(source='brand_id.name')
    category = serializers.ReadOnlyField(source='category_id.name')

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'partnumber',
            'name',
            'brand',
            'category',
            'quantity',
        ]


class SparepartSerializers(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False,
        allow_empty_file=True,
        use_url=True,
        validators=[validate_image_size,
                    FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'name',
            'partnumber',
            'quantity',
            'category_id',
            'motor_type',
            'sparepart_type',
            'brand_id',
            'price',
            'workshop_price',
            'install_price',
            'storage_id',
            'image',
        ]


class SalesDetailSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart', 'quantity', 'is_workshop', 'total_price']

    def get_total_price(self, obj):
        if obj.is_workshop:
            return int(obj.quantity * obj.sparepart_id.workshop_price)
        return int(obj.quantity * obj.sparepart_id.price)


class SalesSerializers(serializers.ModelSerializer):
    content = SalesDetailSerializers(many=True, source='sales_detail_set')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    contact = serializers.ReadOnlyField(source='customer_id.contact')
    total_price_sales = serializers.SerializerMethodField()

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'customer',
            'contact',
            'total_price_sales',
            'is_paid_off',
            'deposit',
            'content'
        ]

    def get_total_price_sales(self, obj):
        sales_serializer = SalesDetailSerializers(obj.sales_detail_set, many=True)
        total_price = 0
        for sales in sales_serializer.data:
            total_price += sales['total_price']
        return total_price


class SalesDetailManagementSerializers(serializers.ModelSerializer):
    sales_detail_id = serializers.IntegerField(required=False)

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart_id', 'quantity', 'is_workshop']


class SalesManagementSerializers(serializers.ModelSerializer):
    content = SalesDetailManagementSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'customer_id',
            'is_paid_off',
            'deposit',
            'content'
        ]

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
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.is_paid_off = validated_data.get('is_paid_off', instance.is_paid_off)
        instance.deposit = validated_data.get('deposit', instance.deposit)

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

        instance.save()

        return instance


class RestockDetailSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Restock_detail
        fields = ['restock_detail_id', 'sparepart', 'individual_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return int(obj.quantity * obj.individual_price)


class RestockSerializers(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    supplier_contact = serializers.ReadOnlyField(source='supplier_id.contact')
    salesman = serializers.ReadOnlyField(source='salesman_id.name')
    salesman_contact = serializers.ReadOnlyField(source='salesman_id.contact')
    content = RestockDetailSerializers(many=True, source='restock_detail_set')
    total_restock_cost = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'no_faktur',
            'due_date',
            'supplier',
            'supplier_contact',
            'salesman',
            'salesman_contact',
            'total_restock_cost',
            'is_paid_off',
            'deposit',
            'content'
        ]

    def get_total_restock_cost(self, obj):
        restock_serializers = RestockDetailSerializers(obj.restock_detail_set, many=True)
        total = 0
        for restock in restock_serializers.data:
            total += int(restock['individual_price']) * restock['quantity']
        return total


class RestockDetailManagementSerializers(serializers.ModelSerializer):
    restock_detail_id = serializers.IntegerField(required=False)

    class Meta:
        model = Restock_detail
        fields = ['restock_detail_id', 'sparepart_id', 'individual_price', 'quantity']


class RestockManagementSerializers(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%d-%m-%Y")
    content = RestockDetailManagementSerializers(many=True, source='restock_detail_set')

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'no_faktur',
            'due_date',
            'supplier_id',
            'salesman_id',
            'is_paid_off',
            'deposit',
            'content'
        ]

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
        instance.deposit = validated_data.get('deposit', instance.deposit)

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

        instance.save()

        return instance


class SupplierSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['supplier_id', 'name', 'contact']


class SupplierManagementSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'supplier_id',
            'name',
            'contact',
            'rekening_number',
            'rekening_name',
            'rekening_bank'
        ]


class SalesReportSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    contact = serializers.ReadOnlyField(source='customer_id.contact')
    total_price_sales = serializers.SerializerMethodField()

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'admin',
            'created_at',
            'updated_at',
            'customer',
            'contact',
            'total_price_sales',
            'is_paid_off',
            'deposit',
        ]

    def get_total_price_sales(self, obj):
        sales_serializer = SalesDetailSerializers(obj.sales_detail_set, many=True)
        total_price = 0
        for sales in sales_serializer.data:
            total_price += sales['total_price']
        return total_price


class SalesReportDetailSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    contact = serializers.ReadOnlyField(source='customer_id.contact')
    content = SalesDetailSerializers(many=True, source='sales_detail_set')
    total_price_sales = serializers.SerializerMethodField()

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'admin',
            'created_at',
            'updated_at',
            'customer',
            'contact',
            'total_price_sales',
            'is_paid_off',
            'deposit',
            'content',
        ]

    def get_total_price_sales(self, obj):
        sales_serializer = SalesDetailSerializers(obj.sales_detail_set, many=True)
        total_price = 0
        for sales in sales_serializer.data:
            total_price += sales['total_price']
        return total_price


class RestockReportSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    supplier_contact = serializers.ReadOnlyField(source='supplier_id.contact')
    salesman = serializers.ReadOnlyField(source='salesman_id.name')
    salesman_contact = serializers.ReadOnlyField(source='salesman_id.contact')
    total_restock_cost = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'admin',
            'created_at',
            'updated_at',
            'no_faktur',
            'total_restock_cost',
            'is_paid_off',
            'deposit',
            'due_date',
            'supplier',
            'supplier_contact',
            'salesman',
            'salesman_contact',
        ]

    def get_total_restock_cost(self, obj):
        restock_serializers = RestockDetailSerializers(obj.restock_detail_set, many=True)
        total = 0
        for restock in restock_serializers.data:
            total += int(restock['individual_price']) * restock['quantity']
        return total


class RestockReportDetailSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    supplier_contact = serializers.ReadOnlyField(source='supplier_id.contact')
    salesman = serializers.ReadOnlyField(source='salesman_id.name')
    salesman_contact = serializers.ReadOnlyField(source='salesman_id.contact')
    content = RestockDetailSerializers(many=True, source='restock_detail_set')
    total_restock_cost = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'admin',
            'created_at',
            'updated_at',
            'no_faktur',
            'total_restock_cost',
            'is_paid_off',
            'deposit',
            'due_date',
            'supplier',
            'supplier_contact',
            'salesman',
            'salesman_contact',
            'content',
        ]

    def get_total_restock_cost(self, obj):
        restock_serializers = RestockDetailSerializers(obj.restock_detail_set, many=True)
        total = 0
        for restock in restock_serializers.data:
            total += int(restock['individual_price']) * restock['quantity']
        return total


class ProfileSerializers(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user_id.email')
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = Profile
        fields = ['name', 'email', 'contact', 'address', 'role']


class ProfileUpdateSerializers(serializers.ModelSerializer):
    username = serializers.CharField(source='user_id.username')
    email = serializers.EmailField(source='user_id.email')

    class Meta:
        model = Profile
        fields = ['name', 'contact', 'address', 'email', 'username']

    def update(self, instance, validated_data):
        # get email and assigning to user instance
        user_data = validated_data.pop('user_id')

        user = instance.user_id
        user.email = user_data.get('email', user.email)
        user.username = user_data.get('username', user.username)
        user.save()

        # Assigning to profile instance
        instance.name = validated_data.get('name', instance.name)
        instance.contact = validated_data.get('contact', instance.contact)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        return instance


class LogSerializers(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user_id.profile.name')
    log_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    operation = serializers.ReadOnlyField(source='get_operation_display')

    class Meta:
        model = Logs
        fields = ['log_id', 'log_at', 'user', 'table', 'operation']


class AdminSerializers(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    contact = serializers.CharField(source='profile.contact')

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'contact']


class AdminManagementSerializers(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    contact = serializers.CharField(source='profile.contact')
    address = serializers.CharField(source='profile.address')
    password_2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'username',
            'contact',
            'address',
            'password',
            'password_2'
        ]

    def create(self, validated_data):
        # remove password_2 data
        validated_data.pop('password_2')

        # get the profile field data
        profile_data = validated_data.pop('profile')

        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user_id=user, **profile_data)

        return user


class AdminUpdateSerializers(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    contact = serializers.CharField(source='profile.contact')
    address = serializers.CharField(source='profile.address')

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'contact', 'address']

    def update(self, instance, validated_data):
        # get the profile field data
        profile_data = validated_data.pop('profile')

        # assigning user data
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # assigning profile data
        profile = instance.profile
        profile.name = profile_data.get('name', profile.name)
        profile.contact = profile_data.get('contact', profile.contact)
        profile.address = profile_data.get('address', profile.address)
        profile.save()

        return instance


class ServiceReportSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    mechanic = serializers.ReadOnlyField(source='mechanic_id.name')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    customer_contact = serializers.ReadOnlyField(source='customer_id.contact')
    total_price_of_service = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'service_id',
            'admin',
            'created_at',
            'updated_at',
            'police_number',
            'mechanic',
            'customer',
            'customer_contact',
            'total_price_of_service',
            'is_paid_off',
            'deposit',
            'discount'
        ]

    def get_total_price_of_service(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        total_price = 0
        for sparepart in sparepart_serializer.data:
            total_price += sparepart['total_price']
        for action in action_serializer.data:
            total_price += int(action['cost'])
        return total_price - int(obj.discount)


class ServiceActionSerializers(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='name')

    class Meta:
        model = Service_action
        fields = ['service_action_id', 'service_name', 'cost']


class ServiceSparepartSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Service_sparepart
        fields = ['service_sparepart_id', 'sparepart', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return int(obj.quantity * obj.sparepart_id.install_price)


class ServiceReportDetailSerializers(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(source='user_id.profile.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    mechanic = serializers.ReadOnlyField(source='mechanic_id.name')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    customer_contact = serializers.ReadOnlyField(source='customer_id.contact')
    service_actions = ServiceActionSerializers(many=True, source='service_action_set')
    service_spareparts = ServiceSparepartSerializers(many=True, source='service_sparepart_set')
    total_price_of_service = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'service_id',
            'admin',
            'created_at',
            'updated_at',
            'police_number',
            'mechanic',
            'customer',
            'customer_contact',
            'total_price_of_service',
            'is_paid_off',
            'deposit',
            'discount',
            'service_actions',
            'service_spareparts',
        ]

    def get_total_price_of_service(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        total_price = 0
        for sparepart in sparepart_serializer.data:
            total_price += sparepart['total_price']
        for action in action_serializer.data:
            total_price += int(action['cost'])
        return total_price - int(obj.discount)


class ServiceSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    mechanic = serializers.ReadOnlyField(source='mechanic_id.name')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    customer_contact = serializers.ReadOnlyField(source='customer_id.contact')
    service_actions = ServiceActionSerializers(many=True, source='service_action_set')
    service_spareparts = ServiceSparepartSerializers(many=True, source='service_sparepart_set')
    total_price_of_service = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'service_id',
            'created_at',
            'police_number',
            'mechanic',
            'customer',
            'customer_contact',
            'total_price_of_service',
            'is_paid_off',
            'deposit',
            'discount',
            'service_actions',
            'service_spareparts'
        ]

    def get_total_price_of_service(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        total_price = 0
        for sparepart in sparepart_serializer.data:
            total_price += sparepart['total_price']
        for action in action_serializer.data:
            total_price += int(action['cost'])
        return total_price - int(obj.discount)


class ServiceActionManagementSerializers(serializers.ModelSerializer):
    service_action_id = serializers.IntegerField(required=False)
    service_name = serializers.CharField(source='name')

    class Meta:
        model = Service_action
        fields = ['service_action_id', 'service_name', 'cost']


class ServiceSparepartManagementSerializers(serializers.ModelSerializer):
    service_sparepart_id = serializers.IntegerField(required=False)

    class Meta:
        model = Service_sparepart
        fields = ['service_sparepart_id', 'sparepart_id', 'quantity']


class ServiceManagementSerializers(serializers.ModelSerializer):
    service_actions = ServiceActionManagementSerializers(many=True, source='service_action_set')
    service_spareparts = ServiceSparepartManagementSerializers(many=True, source='service_sparepart_set')

    class Meta:
        model = Service
        fields = [
            'service_id',
            'mechanic_id',
            'customer_id',
            'police_number',
            'motor_type',
            'is_paid_off',
            'deposit',
            'discount',
            'service_actions',
            'service_spareparts'
        ]

    def create(self, validated_data):
        # get the service actions nested objects list
        action_details = validated_data.pop('service_action_set')

        # get the service spareparts nested objects list
        sparepart_details = validated_data.pop('service_sparepart_set')

        # create service data / instance
        service = Service.objects.create(**validated_data)

        # create service action data / instance
        for detail in action_details:
            try:
                detail.pop('service_action_id')
            except Exception:
                pass
            Service_action.objects.create(service_id=service, **detail)

        # create service sparepart data / instance
        for detail in sparepart_details:
            try:
                detail.pop('service_sparepart_id')
            except Exception:
                pass
            Service_sparepart.objects.create(service_id=service, **detail)

        return service

    def update(self, instance, validated_data):
        # get the service actions nested objects list
        action_details = validated_data.pop('service_action_set')

        # get the service spareparts nested objects list
        sparepart_details = validated_data.pop('service_sparepart_set')

        # Assigning input (validated_data) to object (instance) if there is no data using default object
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.mechanic_id = validated_data.get('mechanic_id', instance.mechanic_id)
        instance.police_number = validated_data.get('police_number', instance.police_number)
        instance.motor_type = validated_data.get('motor_type', instance.motor_type)
        instance.is_paid_off = validated_data.get('is_paid_off', instance.is_paid_off)
        instance.deposit = validated_data.get('deposit', instance.deposit)
        instance.discount = validated_data.get('discount', instance.discount)

        # get all service action nested objects related with this instance
        # and make a dict(id, object)
        action_dict = dict((i.service_action_id, i) for i in instance.service_action_set.all())

        # Updating service actions of particular service
        for validated_detail in action_details:
            if 'service_action_id' in validated_detail:
                # if exists service_action_id remove from the dict and update
                detail = action_dict.pop(validated_detail['service_action_id'])

                # remove service_action_id from validated data as we don't require it.
                validated_detail.pop('service_action_id')

                # loop through the rest of keys in validated data to assign it to its respective field
                for key in validated_detail.keys():
                    setattr(detail, key, validated_detail[key])

                detail.save()
            else:
                Service_action.objects.create(service_id=instance, **validated_detail)

        # delete remaining service action elements because they're not present in update call
        if len(action_dict) > 0:
            for detail in action_dict.values():
                detail.delete()

        # get all service sparepart nested objects related with this instance
        # and make a dict(id, object)
        sparepart_dict = dict((i.service_sparepart_id, i) for i in instance.service_sparepart_set.all())

        # Updating service spareparts of particular service
        for validated_detail in sparepart_details:
            if 'service_sparepart_id' in validated_detail:
                # if exists service_sparepart_id remove from the dict and update
                detail = sparepart_dict.pop(validated_detail['service_sparepart_id'])

                # remove service_sparepart_id from validated data as we don't require it.
                validated_detail.pop('service_sparepart_id')

                # loop through the rest of keys in validated data to assign it to its respective field
                for key in validated_detail.keys():
                    setattr(detail, key, validated_detail[key])

                detail.save()
            else:
                Service_sparepart.objects.create(service_id=instance, **validated_detail)

        # delete remaining service sparepart elements because they're not present in update call
        if len(sparepart_dict) > 0:
            for detail in sparepart_dict.values():
                detail.delete()

        instance.save()

        return instance


class StorageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['storage_id', 'code', 'location', 'is_full']


class BrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand_id', 'name']


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name']


class CustomerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'contact', 'number_of_service', 'total_payment']


class MechanicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Mechanic
        fields = ['mechanic_id', 'name', 'contact', 'address']


class SalesmanSerializers(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source='supplier_id.name')

    class Meta:
        model = Salesman
        fields = ['salesman_id', 'name', 'contact', 'supplier', 'responsibility']


class SalesmanManagementSerializers(serializers.ModelSerializer):
    class Meta:
        model = Salesman
        fields = ['salesman_id', 'name', 'contact', 'supplier_id', 'responsibility']


class RestockDueSerializers(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source='supplier_id.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    remaining_payment = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'no_faktur',
            'created_at',
            'supplier',
            'remaining_payment',
            'due_date'
        ]

    def get_remaining_payment(self, obj):
        restock_serializers = RestockDetailSerializers(obj.restock_detail_set, many=True)
        total = 0
        for restock in restock_serializers.data:
            total += int(restock['individual_price']) * restock['quantity']
        remaining_payment = total - int(obj.deposit)
        return remaining_payment


class SparepartOnLimitSerializers(serializers.ModelSerializer):
    brand = serializers.ReadOnlyField(source='brand_id.name')
    stock = serializers.ReadOnlyField(source='quantity')

    class Meta:
        model = Sparepart
        fields = ['sparepart_id', 'partnumber', 'name', 'brand', 'stock']


class SalesDetailWithDateSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = Sales_detail
        fields = '__all__'


class SparepartMostSoldSerializers(serializers.ModelSerializer):
    brand = serializers.ReadOnlyField(source='brand_id.name')
    total_sold = serializers.SerializerMethodField()

    class Meta:
        model = Sparepart
        fields = ['sparepart_id', 'partnumber', 'name', 'brand', 'total_sold']

    def get_total_sold(self, obj):
        sales_detail = SalesDetailWithDateSerializers(obj.sales_detail_set, many=True)
        total_sold = 0
        for detail in sales_detail.data:
            if int(detail['created_at'].split('-')[1]) == date.today().month:
                total_sold += detail['quantity']
        return total_sold


class ServiceSparepartWithDateSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = Service_sparepart
        fields = '__all__'


class SparepartMostUsedSerializers(serializers.ModelSerializer):
    brand = serializers.ReadOnlyField(source='brand_id.name')
    total_used = serializers.SerializerMethodField()

    class Meta:
        model = Sparepart
        fields = ['sparepart_id', 'partnumber', 'name', 'brand', 'total_used']

    def get_total_used(self, obj):
        services_detail = ServiceSparepartWithDateSerializers(obj.service_sparepart_set, many=True)
        total_used = 0
        for detail in services_detail.data:
            if int(detail['created_at'].split('-')[1]) == date.today().month:
                total_used += detail['quantity']
        return total_used


class SalesRevenueSerializers(serializers.ModelSerializer):
    revenue = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%d-%m-%Y')

    class Meta:
        model = Sales
        fields = ['sales_id', 'revenue', 'created_at']

    def get_revenue(self, obj):
        sales_serializer = SalesDetailSerializers(obj.sales_detail_set, many=True)
        revenue = 0
        for sales in sales_serializer.data:
            revenue += sales['total_price']
        return revenue


class ServiceRevenueSerializers(serializers.ModelSerializer):
    revenue = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%d-%m-%Y')

    class Meta:
        model = Service
        fields = ['service_id', 'revenue', 'created_at']

    def get_revenue(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        revenue = 0
        for sparepart in sparepart_serializer.data:
            revenue += sparepart['total_price']
        for action in action_serializer.data:
            revenue += int(action['cost'])
        return revenue - int(obj.discount)


class RestockExpenditureSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y')
    expenditure = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = ['restock_id', 'expenditure', 'created_at']

    def get_expenditure(self, obj):
        restock_serializers = RestockDetailSerializers(obj.restock_detail_set, many=True)
        expenditure = 0
        for restock in restock_serializers.data:
            expenditure += int(restock['individual_price']) * restock['quantity']
        return expenditure
