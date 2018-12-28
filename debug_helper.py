import telegram
from profiles.models import TelegramBotSettings, QuickRestoApi, OfdruApi, KonturOfdApi
from data_sync_bot.api_manager.ofdru_api import OFDruConnector
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector

telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
pp = telegram.utils.request.Request(proxy_url='https://10.0.2.2:1080')
telegram = telegram.Bot(token=telegram_sett.token, request=pp)

quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
kontur_sett = KonturOfdApi.objects.get(name='KonturOFD_Dzen')

ofdru_conn = OFDruConnector(setting_id=1, infokkt_id=1)
rp = ofdru_conn.get_closedshift_receipts(67)
rp_rec = ofdru_conn.get_recepit_info('c57ff333-82f5-3e79-644c-e9050cb3f79b')