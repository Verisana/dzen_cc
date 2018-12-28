from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import Profile, QuickRestoApi, TelegramBotSettings, OfdruApi, KonturOfdApi, InfoKKT


class ProfileChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Profile


class ProfileAdmin(UserAdmin):
    form = ProfileChangeForm


class InfoKKTAdmin(admin.ModelAdmin):
    fields = [field.name for field in InfoKKT._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in InfoKKT._meta.fields if field.name != 'id']


class QuickRestoApiAdmin(admin.ModelAdmin):
    # Include all fields except id and created_at
    fields = [field.name for field in QuickRestoApi._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in QuickRestoApi._meta.fields if field.name != 'id']


class OfdruApiAdmin(admin.ModelAdmin):
    fields = [field.name for field in OfdruApi._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in OfdruApi._meta.fields if field.name != 'id']


class KonturOfdApiAdmin(admin.ModelAdmin):
    fields = [field.name for field in KonturOfdApi._meta.fields if field.name != 'id' and field.name != 'created_at']
    list_display = [field.name for field in KonturOfdApi._meta.fields if field.name != 'id']


class TelegramBotSettingsAdmin(admin.ModelAdmin):
    fields = [field.name for field in TelegramBotSettings._meta.fields if field.name != 'id']
    list_display = [field.name for field in TelegramBotSettings._meta.fields if field.name != 'id']


admin.site.register(QuickRestoApi, QuickRestoApiAdmin)
admin.site.register(OfdruApi, OfdruApiAdmin)
admin.site.register(KonturOfdApi, KonturOfdApiAdmin)
admin.site.register(InfoKKT, InfoKKTAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TelegramBotSettings, TelegramBotSettingsAdmin)