import telegram
import json
import sys
from profiles.models import TelegramBotSettings, QuickRestoApi
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
from data_sync_bot.models import GoodsBase


telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
telegram = telegram.Bot(token=telegram_sett.token)

quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
quickresto_conn = QuickRestoConnector(setting_id=1)

def refresh_data():
    all_goods = GoodsBase.objects.all()
    try:
        tree_dishes = json.loads(quickresto_conn.tree_all_dish_objects().text)
    except:
        message = f'Error in "sync_database"\nException: {sys.exc_info()[0]}'
        telegram.send_message(chat_id=telegram_sett.chat_emerg, text=message)
        raise sys.exc_info()[0]
    return all_goods, tree_dishes

all_goods, tree_dishes = refresh_data()

def check_internal_structure():
    pass

def add_new_entries():
    check_internal_structure()

def delete_excess_entries():
    check_internal_structure()

def init_entries_comparason():
    quickresto_entries = 0
    for tree_dishe in tree_dishes:
        if 'Category' not in tree_dishe['className']:
            quickresto_entries += 1
    diff_in_entries = quickresto_entries - len(all_goods)
    if diff_in_entries == 0:
        check_internal_structure()
    elif diff_in_entries > 0:
        add_new_entries()
    elif diff_in_entries < 0:
        delete_excess_entries()

init_entries_comparason()
