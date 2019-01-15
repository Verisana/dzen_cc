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
    all_goods = GoodsBase.objects.all().order_by('quickresto_id')
    try:
        tree_dishes = json.loads(quickresto_conn.tree_all_dish_objects().text)
    except:
        message = f'Error in "sync_database"\nException: {sys.exc_info()[0]}'
        telegram.send_message(chat_id=telegram_sett.chat_emerg, text=message)
        raise sys.exc_info()[0]
    return all_goods, tree_dishes

def get_all_data():
    data_for_creation = []
    for tree_dishe in tree_dishes:
        if 'Category' not in tree_dishe['className']:
            data_for_creation.append([tree_dishe['name']])
    return data_for_creation

def standartize_all_data():
    dish_by_id = {}
    data_to_create = []

    #Copy all dishes to get it by IDs
    for tree_dishe in tree_dishes:
        dish_by_id[tree_dishe['id']] = [tree_dishe['name'], tree_dishe['className']]

    #
    for tree_dishe in tree_dishes:
        if 'Category' not in tree_dishe['className']:
            info = {
                'dish_name': tree_dishe['name'],
                'under_group_name': dish_by_id[tree_dishe['parentItem']['id']][0],
                'group_name':       dish_by_id[tree_dishe['parentItem']['id']][0],
                'keyword_ident': tree_dishe['itemTitle'],
                'quickresto_id': tree_dishe['id'],
            }
            for i in tree_dishes:
                if info['under_group_name'] == i['name']:
                    info['group_name'] = dish_by_id[i['parentItem']['id']][0]
                    break
            data_to_create.append(info)
    return data_to_create



def update_database(data_to_update):
    for entry in data_to_update:
        GoodsBase.objects.update_or_create(
            quickresto_id=entry['quickresto_id'],
            defaults={
                'dish_name': entry['dish_name'],
                'under_group_name': entry['under_group_name'],
                'group_name': entry['group_name'],
                'keyword_ident': entry['keyword_ident'],
            }
        )


all_goods, tree_dishes = refresh_data()
data_to_update = standartize_all_data()
update_database(data_to_update)