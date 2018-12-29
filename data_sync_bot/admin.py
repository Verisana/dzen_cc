from django.contrib import admin
from data_sync_bot.models import GoodsBase, GoodsToSale, SalesData, PlacesToSell, PlacePriceModificator


class PlacesToSellAdmin(admin.ModelAdmin):
    fields = [field.name for field in PlacesToSell._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in PlacesToSell._meta.fields if field.name != 'id']


class PlacePriceModificatorAdmin(admin.ModelAdmin):
    fields = [field.name for field in PlacePriceModificator._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in PlacePriceModificator._meta.fields if field.name != 'id']


class GoodsBaseAdmin(admin.ModelAdmin):
    fields = [field.name for field in GoodsBase._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in GoodsBase._meta.fields if field.name != 'id']


class GoodsToSaleAdmin(admin.ModelAdmin):
    fields = [field.name for field in GoodsToSale._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in GoodsToSale._meta.fields if field.name != 'id']


class SalesDataAdmin(admin.ModelAdmin):
    fields = [field.name for field in SalesData._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in SalesData._meta.fields if field.name != 'id']


admin.site.register(PlacesToSell, PlacesToSellAdmin)
admin.site.register(PlacePriceModificator, PlacePriceModificatorAdmin)
admin.site.register(GoodsBase, GoodsBaseAdmin)
admin.site.register(GoodsToSale, GoodsToSaleAdmin)
admin.site.register(SalesData, SalesDataAdmin)