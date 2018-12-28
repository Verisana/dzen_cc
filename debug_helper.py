import telegram
from profiles.models import TelegramBotSettings, QuickRestoApi, OfdruApi, KonturOfdApi


telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
pp = telegram.utils.request.Request(proxy_url='https://10.0.2.2:1080')
telegram = telegram.Bot(token=telegram_sett.token, request=pp)

quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
kontur_sett = KonturOfdApi.objects.get(name='KonturOFD_Dzen')