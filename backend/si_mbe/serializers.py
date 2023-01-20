from datetime import date
from django.contrib.auth.models import User
from rest_framework import serializers
from si_mbe.models import (Brand, Category, Customer, Logs, Profile, Restock,
                           Restock_detail, Sales, Sales_detail, Service,
                           Service_action, Service_sparepart, Sparepart,
                           Supplier, Mechanic, Salesman)
from si_mbe.validators import CustomerValidationError, CustomerConflictError


class HomeSerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    brand = serializers.ChoiceField(Brand.objects.all(), required=False)
    category = serializers.ChoiceField(Category.objects.all(), required=False)
    motor_type = serializers.CharField(required=False)


class SearchSparepartSerializers(serializers.ModelSerializer):
    """
    serializers for searching sparepart
    """
    brand = serializers.ReadOnlyField(source='brand_id.name')
    category = serializers.ReadOnlyField(source='category_id.name')

    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
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
            'storage_code',
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
    class Meta:
        model = Sparepart
        fields = [
            'sparepart_id',
            'name',
            'partnumber',
            'quantity',
            'storage_code',
            'category_id',
            'motor_type',
            'sparepart_type',
            'brand_id',
            'price',
            'workshop_price',
            'install_price',
        ]


class SalesDetailSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        # Check if workshop is true
        if obj.sales_id.is_workshop:
            # calculate with workshop price
            return int(obj.quantity * obj.sparepart_id.workshop_price)

        # calculate with normal price
        return int(obj.quantity * obj.sparepart_id.price)


class SalesSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    total_price_sales = serializers.SerializerMethodField()
    content = SalesDetailSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'created_at',
            'customer',
            'total_price_sales',
            'is_paid_off',
            'deposit',
            'content'
        ]

    def get_total_price_sales(self, obj):
        # Getting all sales_detail data related to the sales
        sales_serializer = SalesDetailSerializers(obj.sales_detail_set, many=True)
        total_price = 0

        # calculating total price by looping throught sales_detail list
        for sales in sales_serializer.data:
            total_price += sales['sub_total']
        return total_price


class SalesDetailManagementSerializers(serializers.ModelSerializer):
    sales_detail_id = serializers.IntegerField(required=False)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart_id', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        # Check if workshop is true
        if obj.sales_id.is_workshop:
            # calculate with workshop price
            return int(obj.quantity * obj.sparepart_id.workshop_price)

        # calculate with normal price
        return int(obj.quantity * obj.sparepart_id.price)


class SalesManagementSerializers(serializers.ModelSerializer):
    customer_name = serializers.CharField(max_length=30, write_only=True, required=False)
    customer_contact = serializers.CharField(max_length=15, write_only=True, required=False)
    total_quantity_sales = serializers.SerializerMethodField()
    total_price_sales = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()
    is_paid_off = serializers.SerializerMethodField()
    content = SalesDetailManagementSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'customer_id',
            'customer_name',
            'customer_contact',
            'is_workshop',
            'deposit',
            'total_quantity_sales',
            'total_price_sales',
            'change',
            'remaining_payment',
            'is_paid_off',
            'content'
        ]

    def get_total_quantity_sales(self, obj):
        # Getting all sales_detail data related to the sales
        sales_serializer = SalesDetailManagementSerializers(obj.sales_detail_set, many=True)

        # calculating total quantity by looping throught sales_detail list
        quantity = 0
        for sales in sales_serializer.data:
            quantity += sales['quantity']
        return quantity

    def get_total_price_sales(self, obj):
        # Getting all sales_detail data related to the sales
        sales_serializer = SalesDetailManagementSerializers(obj.sales_detail_set, many=True)

        # calculating total price by looping throught sales_detail list
        total_price = 0
        for sales in sales_serializer.data:
            total_price += sales['sub_total']
        return total_price

    def get_change(self, obj):
        # Getting total_price using class method
        total_price = self.get_total_price_sales(obj)

        change = int(obj.deposit) - total_price

        # Check if change is greater then 0, if yes return that amount
        # else return 0, because change can't be display as negative
        if change > 0:
            return change
        return 0

    def get_remaining_payment(self, obj):
        # Getting total_price using class method
        total_price = self.get_total_price_sales(obj)

        # Calculating remaining_payment subtracting total_price with deposit
        total = total_price - int(obj.deposit)

        # Check if remaining payment is greater then 0, if yes return that amount
        # else return 0, because remaining payment can't be display as negative
        if total > 0:
            return total
        return 0

    def get_is_paid_off(self, obj):
        # Getting remaining payment value using class method
        remaining_payment = self.get_remaining_payment(obj)

        # Check if remaining payment is eqaul to 0,
        # then set paid off status as True (paid)
        if remaining_payment == 0:
            return True
        return False

    def create(self, validated_data):
        # Get the customer information from validated_data if there none get as None
        customer_id = validated_data.get('customer_id', None)
        customer_name = validated_data.pop('customer_name', None)
        customer_contact = validated_data.pop('customer_contact', None)

        # check if user send new customer name must include contact and vise versa
        if (customer_name is not None) ^ (customer_contact is not None):
            raise CustomerValidationError(
                customer_name=customer_name,
                customer_contact=customer_contact,
                serializer=self
            )
        # check if user fills both old customer field and new customer fields
        elif all((customer_id is not None, customer_contact is not None, customer_name is not None)):
            raise CustomerConflictError(serializer=self)

        # If user send new customer data and customer_id has't register in database,
        # create new customer data in database
        if all((customer_id is None, customer_contact is not None, customer_name is not None)):
            # Create dict of the new customer name and contact
            customer_detail = {}
            customer_detail['name'] = customer_name
            customer_detail['contact'] = customer_contact

            # Create new customer in database
            customer = Customer.objects.create(**customer_detail)

            # send the newly created customer instance to the validated_data
            validated_data['customer_id'] = customer

        # get the nested objects list
        details = validated_data.pop('sales_detail_set')

        # Calculate total_sales_price
        total_sales_price = 0
        for detail in details:
            if validated_data['is_workshop']:
                total_sales_price += int(detail['sparepart_id'].workshop_price) * detail['quantity']
            else:
                total_sales_price += int(detail['sparepart_id'].price) * detail['quantity']

        # Set is_paid_off based on deposit and total_sales_price
        if validated_data['deposit'] < total_sales_price:
            validated_data['is_paid_off'] = False
        else:
            validated_data['is_paid_off'] = True

        # Creating new sales object using all validated data
        sales = Sales.objects.create(**validated_data)

        # Creating all sales_detail object related to the sales
        # by looping throught sales detail list of dict
        for details in details:
            # Remove sales_detail_id because in create operations we didn't need it
            try:
                details.pop('sales_detail_id')
            except Exception:
                pass
            Sales_detail.objects.create(sales_id=sales, **details)
        return sales

    def update(self, instance, validated_data):
        # get the nested objects list
        validated_details = validated_data.pop('sales_detail_set')

        # Remove customer name and contact because in update operations we didn't need it
        try:
            validated_data.pop('customer_name')
            validated_data.pop('customer_contact')
        except Exception:
            pass

        # Assigning input (validated_data) to object (instance)
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.is_paid_off = validated_data.get('is_paid_off', instance.is_paid_off)
        instance.deposit = validated_data.get('deposit', instance.deposit)
        instance.is_workshop = validated_data.get('is_workshop', instance.deposit)

        # Calculate total_sales_price
        total_sales_price = 0
        for detail in validated_details:
            if validated_data['is_workshop']:
                total_sales_price += int(detail['sparepart_id'].workshop_price) * detail['quantity']
            else:
                total_sales_price += int(detail['sparepart_id'].price) * detail['quantity']

        # Set is_paid_off based on deposit and total_sales_price
        if instance.deposit < total_sales_price:
            instance.is_paid_off = False
        else:
            instance.is_paid_off = True

        # get all nested objects related with this instance and make a dict(id, object)
        details_dict = dict((i.sales_detail_id, i) for i in instance.sales_detail_set.all())

        # Updating all sales_detail object related to the sales
        # by looping throught sales detail list of dict
        for validated_detail in validated_details:
            # Check if exists sales_detail_id
            if 'sales_detail_id' in validated_detail:
                # remove from the dict and update
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
    supplier = serializers.ReadOnlyField(source='salesman_id.supplier_id.name')
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    content = RestockDetailSerializers(many=True, source='restock_detail_set')
    total_restock_cost = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'no_faktur',
            'created_at',
            'supplier',
            'total_restock_cost',
            'is_paid_off',
            'content'
        ]

    def get_total_restock_cost(self, obj):
        # Getting all restock_detail data related to the restock
        restock_detail = RestockDetailSerializers(obj.restock_detail_set, many=True)

        # calculating total price by looping throught restock_detail list
        total = 0
        for restock in restock_detail.data:
            total += int(restock['individual_price']) * restock['quantity']
        return total


class RestockDetailManagementSerializers(serializers.ModelSerializer):
    restock_detail_id = serializers.IntegerField(required=False)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Restock_detail
        fields = ['restock_detail_id', 'sparepart_id', 'individual_price', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        return int(obj.quantity * obj.individual_price)


class RestockManagementSerializers(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%d-%m-%Y")
    supplier = serializers.ReadOnlyField(source='salesman_id.supplier_id.name')
    total_sparepart_quantity = serializers.SerializerMethodField()
    total_restock_cost = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()
    is_paid_off = serializers.SerializerMethodField()
    content = RestockDetailManagementSerializers(many=True, source='restock_detail_set')

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'no_faktur',
            'due_date',
            'salesman_id',
            'supplier',
            'total_sparepart_quantity',
            'total_restock_cost',
            'deposit',
            'remaining_payment',
            'is_paid_off',
            'content'
        ]

    def get_total_sparepart_quantity(self, obj):
        # Getting restock_detail data related to the restock
        restock_detail = RestockDetailManagementSerializers(obj.restock_detail_set, many=True)

        # Calculating amount_of_sparepart by looping trought restock_detail
        total_sparepart_quantity = 0
        for detail in restock_detail.data:
            total_sparepart_quantity += detail['quantity']
        return total_sparepart_quantity

    def get_total_restock_cost(self, obj):
        # Getting restock_detail data related to the restock
        restock_detail = RestockDetailManagementSerializers(obj.restock_detail_set, many=True)

        # Calculating total_restock_cost by looping trought restock_detail
        total_restock_cost = 0
        for restock in restock_detail.data:
            total_restock_cost += restock['sub_total']
        return total_restock_cost

    def get_remaining_payment(self, obj):
        # Getting total_cost data
        total_restock_cost = self.get_total_restock_cost(obj)

        # Calculating remaining_payment subtracting total_cost with deposit
        remaining_payment = total_restock_cost - int(obj.deposit)

        # Check if remaining payment is greater then 0, if yes return that amount
        # else return 0, because remaining payment can't be display as negative
        if remaining_payment < 0:
            return 0
        return remaining_payment

    def get_is_paid_off(self, obj):
        # Getting total_cost data
        total_restock_cost = self.get_total_restock_cost(obj)

        # Check if deposit is less than total_cost if yes then it's still not paid_off yet
        if int(obj.deposit) < total_restock_cost:
            return False
        return True

    def create(self, validated_data):
        # get the nested objects list
        details = validated_data.pop('restock_detail_set')

        # Calculate total_restock_cost
        total_restock_cost = 0
        for detail in details:
            total_restock_cost += int(detail['individual_price']) * detail['quantity']

        # Set is_paid_off based on deposit and total_restock_cost
        if validated_data['deposit'] < total_restock_cost:
            validated_data['is_paid_off'] = False
        else:
            validated_data['is_paid_off'] = True

        # Create restock instance using all validated data
        restock = Restock.objects.create(**validated_data)

        # Creating all restock_detail object related to the restock
        # by looping throught restock detail list of dict
        for details in details:
            # Remove restock_detail_id because in create operations we didn't need it
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
        instance.deposit = validated_data.get('deposit', instance.deposit)

        # Recalculate total_restock_cost
        total_restock_cost = 0
        for detail in validated_details:
            total_restock_cost += int(detail['individual_price']) * detail['quantity']

        # Set is_paid_off based on deposit and total_restock_cost
        if instance.deposit < total_restock_cost:
            instance.is_paid_off = False
        else:
            instance.is_paid_off = True

        # get all nested objects related with this instance and make a dict(id, object)
        details_dict = dict((i.restock_detail_id, i) for i in instance.restock_detail_set.all())

        for validated_detail in validated_details:
            # if exists restock_detail_id
            if 'restock_detail_id' in validated_detail:
                # remove from the dict and update
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
    created_at = serializers.DateTimeField(format='%d-%m-%Y')
    updated_at = serializers.DateTimeField(format='%d-%m-%Y')
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
            total_price += sales['sub_total']
        return total_price


class RestockReportSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y')
    total_restock_cost = serializers.SerializerMethodField()

    class Meta:
        model = Restock
        fields = [
            'restock_id',
            'created_at',
            'total_restock_cost',
            'deposit',
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
    supplier = serializers.ReadOnlyField(source='salesman_id.supplier_id.name')
    supplier_contact = serializers.ReadOnlyField(source='salesman_id.supplier_id.contact')
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
    created_at = serializers.DateTimeField(format='%d-%m-%Y')
    total_service_price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'service_id',
            'created_at',
            'total_service_price',
            'deposit',
            'discount'
        ]

    def get_total_service_price(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        total_price = 0
        for sparepart in sparepart_serializer.data:
            total_price += sparepart['sub_total']
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
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Service_sparepart
        fields = ['service_sparepart_id', 'sparepart', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        return int(obj.quantity * obj.sparepart_id.install_price)


class ServiceSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    mechanic = serializers.ReadOnlyField(source='mechanic_id.name')
    customer = serializers.ReadOnlyField(source='customer_id.name')
    total_service_price = serializers.SerializerMethodField()
    service_actions = ServiceActionSerializers(many=True, source='service_action_set')
    service_spareparts = ServiceSparepartSerializers(many=True, source='service_sparepart_set')

    class Meta:
        model = Service
        fields = [
            'service_id',
            'created_at',
            'customer',
            'mechanic',
            'total_service_price',
            'is_paid_off',
            'service_actions',
            'service_spareparts'
        ]

    def get_total_service_price(self, obj):
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)
        total_price = 0
        for sparepart in sparepart_serializer.data:
            total_price += sparepart['sub_total']
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
    price = serializers.ReadOnlyField(source='sparepart_id.install_price')
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Service_sparepart
        fields = ['service_sparepart_id', 'sparepart_id', 'quantity', 'price', 'sub_total']

    def get_sub_total(self, obj):
        # calculate sub total with install price of sparepart
        return int(obj.quantity * obj.sparepart_id.install_price)


class ServiceManagementSerializers(serializers.ModelSerializer):
    customer_name = serializers.CharField(max_length=30, write_only=True, required=False)
    customer_contact = serializers.CharField(max_length=15, write_only=True, required=False)
    spareparts_amount = serializers.SerializerMethodField()
    sub_total_actions = serializers.SerializerMethodField()
    sub_total_spareparts = serializers.SerializerMethodField()
    total_service_price = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()
    is_paid_off = serializers.SerializerMethodField()
    service_actions = ServiceActionManagementSerializers(many=True, source='service_action_set')
    service_spareparts = ServiceSparepartManagementSerializers(many=True, source='service_sparepart_set')

    class Meta:
        model = Service
        fields = [
            'service_id',
            'mechanic_id',
            'customer_id',
            'customer_name',
            'customer_contact',
            'police_number',
            'motor_type',
            'deposit',
            'spareparts_amount',
            'sub_total_actions',
            'sub_total_spareparts',
            'total_service_price',
            'change',
            'remaining_payment',
            'is_paid_off',
            'service_actions',
            'service_spareparts'
        ]

    def get_spareparts_amount(self, obj):
        # Getting all service_sparepart data related to the service
        service_spareparts = ServiceSparepartManagementSerializers(obj.service_sparepart_set, many=True)

        # calculating total quantity by looping throught service_sparepart list
        sparepart_amounts = 0
        for sparepart in service_spareparts.data:
            sparepart_amounts += sparepart['quantity']
        return sparepart_amounts

    def get_sub_total_actions(self, obj):
        # Getting all service_action data related to the service
        service_action = ServiceActionManagementSerializers(obj.service_action_set, many=True)

        # calculating sub_total by looping throught service_action list
        sub_total = 0
        for action in service_action.data:
            sub_total += int(action['cost'])
        return sub_total

    def get_sub_total_spareparts(self, obj):
        # Getting all service_sparepart data related to the service
        service_spareparts = ServiceSparepartManagementSerializers(obj.service_sparepart_set, many=True)

        # calculating sub_total by looping throught service_sparepart list
        sub_total = 0
        for sparepart in service_spareparts.data:
            sub_total += sparepart['sub_total']
        return sub_total

    def get_total_service_price(self, obj):
        # Getting sub total action and sparepart using class method
        sub_total_action = self.get_sub_total_actions(obj)
        sub_total_sparepart = self.get_sub_total_spareparts(obj)
        return sub_total_action + sub_total_sparepart

    def get_change(self, obj):
        # Getting total service price using class method
        total = self.get_total_service_price(obj)

        change = int(obj.deposit) - total

        # Check if change is greater then 0, if yes return that amount
        # else return 0, because change can't be display as negative
        if change > 0:
            return change
        return 0

    def get_remaining_payment(self, obj):
        # Getting total service price using class method
        total = self.get_total_service_price(obj)

        remaining_payment = total - int(obj.deposit)

        # Check if remaining payment is greater then 0, if yes return that amount
        # else return 0, because remaining payment can't be display as negative
        if remaining_payment > 0:
            return remaining_payment
        return 0

    def get_is_paid_off(self, obj):
        # Getting remaining payment value using class method
        remaining_payment = self.get_remaining_payment(obj)

        # Check if remaining payment is eqaul to 0,
        # then set paid off status as True (paid)
        if remaining_payment == 0:
            return True
        return False

    def create(self, validated_data):
        # Get the customer information from validated_data if there none get as None
        customer_id = validated_data.get('customer_id', None)
        customer_name = validated_data.pop('customer_name', None)
        customer_contact = validated_data.pop('customer_contact', None)

        # check if user send new customer name must include contact and vise versa
        if (customer_name is not None) ^ (customer_contact is not None):
            raise CustomerValidationError(
                customer_name=customer_name,
                customer_contact=customer_contact,
                serializer=self
            )
        # check if user fills both old customer field and new customer fields
        elif all((customer_id is not None, customer_contact is not None, customer_name is not None)):
            raise CustomerConflictError(serializer=self)

        # If user send new customer data and customer_id has't register in database,
        # create new customer data in database
        if all((customer_id is None, customer_contact is not None, customer_name is not None)):
            # Create dict of the new customer name and contact
            customer_detail = {}
            customer_detail['name'] = customer_name
            customer_detail['contact'] = customer_contact

            # Create new customer in database
            customer = Customer.objects.create(**customer_detail)

            # send the newly created customer instance to the validated_data
            validated_data['customer_id'] = customer

        # get the service actions nested objects list
        action_details = validated_data.pop('service_action_set')

        # get the service spareparts nested objects list
        sparepart_details = validated_data.pop('service_sparepart_set')

        # Calculate total_service_price
        total_service_price = 0
        for detail in sparepart_details:
            total_service_price += int(detail['sparepart_id'].install_price) * detail['quantity']

        # Set is_paid_off based on deposit and total_service_price
        if validated_data['deposit'] < total_service_price:
            validated_data['is_paid_off'] = False
        else:
            validated_data['is_paid_off'] = True

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
        # Remove customer name and contact because in update operations we didn't need it
        try:
            validated_data.pop('customer_name')
            validated_data.pop('customer_contact')
        except Exception:
            pass

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

        # Calculate total_service_price
        total_service_price = 0
        for sparepart in sparepart_details:
            total_service_price += int(sparepart['sparepart_id'].install_price) * sparepart['quantity']
        for action in action_details:
            total_service_price += int(action['cost'])

        # Set is_paid_off based on deposit and total_service_price
        if instance.deposit < total_service_price:
            instance.is_paid_off = False
        else:
            instance.is_paid_off = True

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


class BrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand_id', 'name']


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name']


class CustomerSerializers(serializers.ModelSerializer):
    number_of_service = serializers.SerializerMethodField()
    total_payment = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'name',
            'contact',
            'number_of_service',
            'total_payment',
            'remaining_payment'
        ]

    def get_number_of_service(self, obj):
        # Getting service data related to the customer
        services = ServiceSerializers(obj.service_set, many=True)

        # Calculating number of service related to the customer, only current year
        number_of_service = 0
        for service in services.data:
            if str(date.today().year) in service['created_at']:
                number_of_service += 1
        return number_of_service

    def get_total_payment(self, obj):
        # Getting services and sales data, that related to customer
        services = ServiceSerializers(obj.service_set, many=True)
        sales = SalesSerializers(obj.sales_set, many=True)

        # Calculating total_payment by looping trought services and sales data, only current year
        total_payment = 0
        for service in services.data:
            if str(date.today().year) in service['created_at']:
                total_payment += service['total_service_price']
        for sale in sales.data:
            if str(date.today().year) in sale['created_at']:
                total_payment += sale['total_price_sales']
        return total_payment

    def get_remaining_payment(self, obj):
        # Getting total payment
        total_payment = self.get_total_payment(obj)

        # Getting services and sales data, that related to customer
        services = ServiceReportSerializers(obj.service_set, many=True)
        sales = SalesReportSerializers(obj.sales_set, many=True)

        # Calculating deposit by looping trought services and sales data, only current year
        deposit = 0
        for service in services.data:
            if str(date.today().year) in service['created_at']:
                deposit += int(service['deposit'])
        for sale in sales.data:
            if str(date.today().year) in sale['created_at']:
                deposit += int(sale['deposit'])

        # Calculating remaining_payment, then return it if value is positive
        remaining_payment = total_payment - deposit
        if remaining_payment > 0:
            return remaining_payment
        return 0


class CustomerManagementSerializers(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'contact']


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
            revenue += sales['sub_total']
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
            revenue += sparepart['sub_total']
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


class SalesDetailReceiptSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    sub_total = serializers.SerializerMethodField()
    individual_price = serializers.SerializerMethodField()

    class Meta:
        model = Sales_detail
        fields = ['sales_detail_id', 'sparepart', 'quantity', 'individual_price', 'sub_total']

    def get_sub_total(self, obj):
        # Check if workshop is true
        if obj.sales_id.is_workshop:
            # calculate with workshop price
            return int(obj.quantity * obj.sparepart_id.workshop_price)

        # calculate with normal price
        return int(obj.quantity * obj.sparepart_id.price)

    def get_individual_price(self, obj):
        # Check if workshop is true
        if obj.sales_id.is_workshop:
            # return individual sparepart workshop price
            return int(obj.sparepart_id.workshop_price)

        # return individual sparepart normal price
        return int(obj.sparepart_id.price)


class SalesReceiptSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    customer_name = serializers.ReadOnlyField(source='customer_id.name')
    customer_contact = serializers.ReadOnlyField(source='customer_id.contact')
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()
    content = SalesDetailReceiptSerializers(many=True, source='sales_detail_set')

    class Meta:
        model = Sales
        fields = [
            'sales_id',
            'created_at',
            'customer_name',
            'customer_contact',
            'deposit',
            'total_quantity',
            'total_price',
            'change',
            'remaining_payment',
            'is_paid_off',
            'content'
        ]

    def get_total_quantity(self, obj):
        # Getting all sales_detail data related to the sales
        sales_serializer = SalesDetailReceiptSerializers(obj.sales_detail_set, many=True)

        # calculating total quantity by looping throught sales_detail list
        quantity = 0
        for sales in sales_serializer.data:
            quantity += sales['quantity']
        return quantity

    def get_total_price(self, obj):
        # Getting all sales_detail data related to the sales
        sales_serializer = SalesDetailReceiptSerializers(obj.sales_detail_set, many=True)

        # calculating total price by looping throught sales_detail list
        total_price = 0
        for sales in sales_serializer.data:
            total_price += sales['sub_total']
        return total_price

    def get_change(self, obj):
        # Getting total_price using class method
        total_price = self.get_total_price(obj)

        change = int(obj.deposit) - total_price

        # Check if change is greater then 0, if yes return that amount
        # else return 0, because change can't be display as negative
        if change > 0:
            return change
        return 0

    def get_remaining_payment(self, obj):
        # Getting total_price using class method
        total_price = self.get_total_price(obj)

        # Calculating remaining_payment subtracting total_price with deposit
        total = total_price - int(obj.deposit)

        # Check if remaining payment is greater then 0, if yes return that amount
        # else return 0, because remaining payment can't be display as negative
        if total > 0:
            return total
        return 0


class ServiceSparepartReceiptSerializers(serializers.ModelSerializer):
    sparepart = serializers.ReadOnlyField(source='sparepart_id.name')
    individual_price = serializers.ReadOnlyField(source='sparepart_id.install_price')
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Service_sparepart
        fields = ['service_sparepart_id', 'sparepart', 'quantity', 'individual_price', 'sub_total']

    def get_sub_total(self, obj):
        return int(obj.quantity * obj.sparepart_id.install_price)


class ServiceActionReceiptSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service_action
        fields = ['service_action_id', 'name', 'cost']


class ServiceReceiptSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')
    customer_name = serializers.ReadOnlyField(source='customer_id.name')
    total_quantity = serializers.SerializerMethodField()
    sub_total_action = serializers.SerializerMethodField()
    sub_total_part = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    final_total_price = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    remaining_payment = serializers.SerializerMethodField()
    service_spareparts = ServiceSparepartReceiptSerializers(many=True, source='service_sparepart_set')
    service_actions = ServiceActionReceiptSerializers(many=True, source='service_action_set')

    class Meta:
        model = Service
        fields = [
            'service_id',
            'created_at',
            'customer_name',
            'total_quantity',
            'sub_total_part',
            'sub_total_action',
            'total_price',
            'discount',
            'final_total_price',
            'deposit',
            'change',
            'remaining_payment',
            'service_actions',
            'service_spareparts'
        ]

    def get_total_quantity(self, obj):
        # Getting all service_sparepart data related to the service
        service_spareparts = ServiceSparepartManagementSerializers(obj.service_sparepart_set, many=True)

        # calculating total quantity by looping throught service_sparepart list
        sparepart_amounts = 0
        for sparepart in service_spareparts.data:
            sparepart_amounts += sparepart['quantity']
        return sparepart_amounts

    def get_sub_total_part(self, obj):
        # Getting all service_sparepart and service_action data related to the service
        sparepart_serializer = ServiceSparepartSerializers(obj.service_sparepart_set, many=True)

        # calculating total price by looping throught service_sparepart list
        sub_total = 0
        for sparepart in sparepart_serializer.data:
            sub_total += sparepart['sub_total']
        return sub_total

    def get_sub_total_action(self, obj):
        # Getting service_action data related to the service
        action_serializer = ServiceActionSerializers(obj.service_action_set, many=True)

        # calculating total price by looping throught service_action list
        sub_total = 0
        for action in action_serializer.data:
            sub_total += int(action['cost'])
        return sub_total

    def get_total_price(self, obj):
        # Getting all service_sparepart and service_action sub_total using class method
        sub_total_sparepart = self.get_sub_total_part(obj)
        sub_total_action = self.get_sub_total_action(obj)

        total_price = sub_total_sparepart + sub_total_action

        return total_price

    def get_final_total_price(self, obj):
        # Getting total service price using class method
        total_price = self.get_total_price(obj)
        return total_price - int(obj.discount)

    def get_change(self, obj):
        # Getting final total service price using class method
        total = self.get_final_total_price(obj)

        change = int(obj.deposit) - total

        # Check if change is greater then 0, if yes return that amount
        # else return 0, because change can't be display as negative
        if change > 0:
            return change
        return 0

    def get_remaining_payment(self, obj):
        # Getting total service price using class method
        total = self.get_final_total_price(obj)

        remaining_payment = total - int(obj.deposit)

        # Check if remaining payment is greater then 0, if yes return that amount
        # else return 0, because remaining payment can't be display as negative
        if remaining_payment > 0:
            return remaining_payment
        return 0
