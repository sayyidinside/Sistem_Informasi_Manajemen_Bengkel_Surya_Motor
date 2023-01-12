from django.contrib import admin
from si_mbe.models import (Brand, Category, Customer, Logs, Mechanic, Profile,
                           Restock, Restock_detail, Sales, Sales_detail,
                           Salesman, Service, Service_action,
                           Service_sparepart, Sparepart, Supplier)


# Register your models here.
class BrandAdmin(admin.ModelAdmin):
    readonly_fields = ['brand_id']


class LogsAdmin(admin.ModelAdmin):
    readonly_fields = ['log_id']


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['id']


class RestockAdmin(admin.ModelAdmin):
    readonly_fields = ['restock_id']


class RestockDetailAdmin(admin.ModelAdmin):
    readonly_fields = ['restock_detail_id']


class SalesAdmin(admin.ModelAdmin):
    readonly_fields = ['sales_id']


class SalesDetailAdmin(admin.ModelAdmin):
    readonly_fields = ['sales_detail_id']


class SparepartAdmin(admin.ModelAdmin):
    readonly_fields = ['sparepart_id']


class SupplierAdmin(admin.ModelAdmin):
    readonly_fields = ['supplier_id']


class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['category_id']


class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ['customer_id']


class MechanicAdmin(admin.ModelAdmin):
    readonly_fields = ['mechanic_id']


class SalesmanAdmin(admin.ModelAdmin):
    readonly_fields = ['salesman_id']


class ServiceAdmin(admin.ModelAdmin):
    readonly_fields = ['service_id']


class ServiceActionAdmin(admin.ModelAdmin):
    readonly_fields = ['service_action_id']


class ServiceSparepartAdmin(admin.ModelAdmin):
    readonly_fields = ['service_sparepart_id']


admin.site.register(Brand, BrandAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Restock, RestockAdmin)
admin.site.register(Restock_detail, RestockDetailAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(Sales_detail, SalesDetailAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Sparepart, SparepartAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Mechanic, MechanicAdmin)
admin.site.register(Salesman, SalesmanAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Service_action, ServiceActionAdmin)
admin.site.register(Service_sparepart, ServiceSparepartAdmin)
