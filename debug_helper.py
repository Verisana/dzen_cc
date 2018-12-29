import telegram
from profiles.models import TelegramBotSettings, QuickRestoApi, OfdruApi
from data_sync_bot.api_manager.ofdru_api import OFDruConnector
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
import json

telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
pp = telegram.utils.request.Request(proxy_url='https://10.0.2.2:1080')
telegram = telegram.Bot(token=telegram_sett.token, request=pp)

quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')

ofdru_conn = OFDruConnector(setting_id=1, infokkt_id=1)
rp = ofdru_conn.get_closedshift_receipts(68)
date_rec = ofdru_conn.get_daterange_receipts('2018-12-27T00:00', '2018-12-27T23:59 ')
#rp_rec = ofdru_conn.get_recepit_info('defdef94-af80-4177-2852-352932b66cc0')
#rec = json.loads(rp_rec.text)
date_rec = json.loads(date_rec.text)
all_rec = json.loads(rp.text)