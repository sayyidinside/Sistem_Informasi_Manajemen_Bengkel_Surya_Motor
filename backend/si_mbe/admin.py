from django.contrib import admin
from si_mbe.models import (Brand, Logs, Profile, Restock, Restock_detail,
                           Sales, Sales_detail, Sparepart, Storage, Supplier)


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


class StorageAdmin(admin.ModelAdmin):
    readonly_fields = ['storage_id']


class SupplierAdmin(admin.ModelAdmin):
    readonly_fields = ['supplier_id']


admin.site.register(Brand, BrandAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Restock, RestockAdmin)
admin.site.register(Restock_detail, RestockDetailAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(Sales_detail, SalesDetailAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(Sparepart, SparepartAdmin)
