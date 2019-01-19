from django.contrib import admin
from data_sync_bot.models import GoodsBase, GoodsToSale, SalesData, PlacesToSell, PlacePriceModificator, EmployeesList


class PlacesToSellAdmin(admin.ModelAdmin):
    fields = [field.name for field in PlacesToSell._meta.fields if field.name != 'id']
    list_display = [field.name for field in PlacesToSell._meta.fields if field.name != 'id']


class EmployeesListAdmin(admin.ModelAdmin):
    fields = [field.name for field in EmployeesList._meta.fields if field.name != 'id']
    list_display = [field.name for field in EmployeesList._meta.fields if field.name != 'id']


class PlacePriceModificatorAdmin(admin.ModelAdmin):
    fields = [field.name for field in PlacePriceModificator._meta.fields if field.name != 'id']
    list_display = [field.name for field in PlacePriceModificator._meta.fields if field.name != 'id']
    list_filter = ['place_to_sale', 'price']


class GoodsBaseAdmin(admin.ModelAdmin):
    fields = [field.name for field in GoodsBase._meta.fields if field.name != 'id'] + ['base_price']
    filter_horizontal = ['base_price']
    list_filter = ['group_name', 'under_group_name', 'dish_name']
    list_display = [field.name for field in GoodsBase._meta.fields if field.name != 'id']


class GoodsToSaleAdmin(admin.ModelAdmin):
    fields = [field.name for field in GoodsToSale._meta.fields if field.name != 'id']
    list_display = [field.name for field in GoodsToSale._meta.fields if field.name != 'id']


class SalesDataAdmin(admin.ModelAdmin):
    fields = [field.name for field in SalesData._meta.fields if field.name != 'id'] + ['sold_goods']
    filter_horizontal = ['sold_goods']
    list_display = [field.name for field in SalesData._meta.fields if field.name != 'id']
    list_filter = [
        'address',
        'receipt_type',
        'is_fulled',
        'staff_name',
        'payment_type',
        'is_uploaded_quickresto',
        'is_fulled',
    ]
    search_fields = ['shift_number', 'receipt_num']

admin.site.register(PlacesToSell, PlacesToSellAdmin)
admin.site.register(EmployeesList, EmployeesListAdmin)
admin.site.register(PlacePriceModificator, PlacePriceModificatorAdmin)
admin.site.register(GoodsBase, GoodsBaseAdmin)
admin.site.register(GoodsToSale, GoodsToSaleAdmin)
admin.site.register(SalesData, SalesDataAdmin)