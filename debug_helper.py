import telegram
from django.utils import timezone
from profiles.models import TelegramBotSettings, QuickRestoApi, OfdruApi
from data_sync_bot.api_manager.ofdru_api import OFDruConnector
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
from data_sync_bot.receipt_manager.ofd_receipt_saver import OFDReceiptSaver
from data_sync_bot.receipt_manager.quickresto_saver import QuickRestoSaver
from data_sync_bot.models import SalesData
from data_sync_bot.tasks import check_updates
import json



telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
pp = telegram.utils.request.Request(proxy_url='https://10.0.2.2:1080')
telegram = telegram.Bot(token=telegram_sett.token, request=pp)

#QUICKRESTO
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
from django.utils import timezone
from profiles.models import TelegramBotSettings, QuickRestoApi, OfdruApi
from data_sync_bot.receipt_manager.quickresto_saver import QuickRestoSaver

qr_saver = QuickRestoSaver()
qr_saver.update_quikresto()
quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
quickresto_conn = QuickRestoConnector(setting_id=1, place_id=1)

list_dishes = json.loads(quickresto_conn.list_all_dish_objects().text)
tree_dishes = json.loads(quickresto_conn.tree_all_dish_objects().text)

#OFDRU
rec_sav = OFDReceiptSaver()
ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
ofdru_conn = OFDruConnector(setting_id=1, place_id=2)
rp = ofdru_conn.get_closedshift_receipts(400)
rp = ofdru_conn.get_recepit_info_bynum(400, 19)
all_rec = json.loads(rp.text)
rec_sav.create_new_entry_salesdata(all_rec)
date_rec = ofdru_conn.get_daterange_receipts('2018-12-27T00:00', '2018-12-27T23:59 ')
date_rec = json.loads(date_rec.text)
#rp_rec = ofdru_conn.get_recepit_info('defdef94-af80-4177-2852-352932b66cc0')
#rec = json.loads(rp_rec.text)

#CELERY
celery flower -A dzen_cc --loglevel=INFO
celery -A dzen_cc beat -l info
celery -A dzen_cc worker -l info -n check_updates@ubuntu --purge
check_updates()