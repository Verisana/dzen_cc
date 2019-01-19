import telegram
import json
import sys
from profiles.models import TelegramBotSettings, QuickRestoApi
from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
from data_sync_bot.models import GoodsBase, PlacesToSell, PlacePriceModificator


class SyncGoodsInDB:
    def __init__(self, place_id=1):
        self.telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
        self.telegram = telegram.Bot(token=self.telegram_sett.token)

        self.quickresto_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
        self.quickresto_conn = QuickRestoConnector(setting_id=1, place_id=place_id)

        self.all_goods = GoodsBase.objects.all().order_by('quickresto_id')
        try:
            self.tree_dishes = json.loads(self.quickresto_conn.tree_all_dish_objects().text)
        except:
            message = f'Error in "sync_database"\nException: {sys.exc_info()[0]}'
            self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)
            raise sys.exc_info()[0]

    def get_all_data(self):
        data_for_creation = []
        for tree_dishe in self.tree_dishes:
            if 'Category' not in tree_dishe['className']:
                data_for_creation.append([tree_dishe['name']])
        return data_for_creation

    def standartize_all_data(self):
        dish_by_id = {}
        data_to_create = []

        #Copy all dishes to get it by IDs
        for tree_dishe in self.tree_dishes:
            dish_by_id[tree_dishe['id']] = [tree_dishe['name'], tree_dishe['className']]

        for tree_dishe in self.tree_dishes:
            if 'Category' not in tree_dishe['className']:
                price_objects = []
                for prices in tree_dishe['dishSales']:
                    place = PlacesToSell.objects.get(quickresto_place_id=prices['salePlace']['id'])
                    price_object = PlacePriceModificator.objects.update_or_create(
                            place_to_sale=place,
                            price=prices['price'],
                            defaults={
                                'place_to_sale': place,
                                'price': prices['price'],
                            }
                        )[0]
                    price_objects.append(price_object)
                info = {
                    'dish_name': tree_dishe['name'],
                    'under_group_name': dish_by_id[tree_dishe['parentItem']['id']][0],
                    'group_name':       dish_by_id[tree_dishe['parentItem']['id']][0],
                    'keyword_ident': tree_dishe['itemTitle'],
                    'quickresto_id': tree_dishe['id'],
                    'base_price': price_objects,
                }
                for i in self.tree_dishes:
                    if info['under_group_name'] == i['name']:
                        info['group_name'] = dish_by_id[i['parentItem']['id']][0]
                        break
                data_to_create.append(info)
        return data_to_create



    def update_database(self, data_to_update):
        for entry in data_to_update:
            goods_base = GoodsBase.objects.update_or_create(
                    quickresto_id=entry['quickresto_id'],
                    defaults={
                        'dish_name': entry['dish_name'],
                        'under_group_name': entry['under_group_name'],
                        'group_name': entry['group_name'],
                        'keyword_ident': entry['keyword_ident'],
                    }
                )[0]
            goods_base.base_price.set(entry['base_price'])

    def start_sync(self):
        data_to_update = self.standartize_all_data()
        self.update_database(data_to_update)