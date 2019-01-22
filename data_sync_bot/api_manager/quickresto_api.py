import requests
from django.utils import timezone

from data_sync_bot.models import PlacesToSell
from profiles.models import QuickRestoApi


class QuickRestoConnector():
    BASE_URL = 'https://td581.quickresto.ru/platform/online/'
    HEADER = {'content-type': 'application/json', 'Connection': 'keep-alive'}

    def __init__(self, setting_id, place_id):
        self.quickresto_sett = QuickRestoApi.objects.get(id=setting_id)
        self.places_to_sell = PlacesToSell.objects.get(id=place_id)
        self.login = self.quickresto_sett.api_login
        self.password = self.quickresto_sett.api_pass

    def list_all_shifts(self):
        return self.send_request('api/list?moduleName=front.zreport', 'get')

    def open_shift(self, shift_number, employee_id, opened):
        params = {
            'frontId': f'{self.places_to_sell.quickresto_place_id}_{shift_number}',
            'incomplete': True,
            'status': 'OPENED',
            'kkmTerminal': {'id': self.places_to_sell.quickresto_kkm_id},
            'shiftNumber': shift_number,
            'openedEmployee': {'id': employee_id},
            'opened': opened.isoformat().replace('+00:00', 'Z'),
            'salePlace': {'id': self.places_to_sell.quickresto_place_id},
        }
        return self.send_request('api/create?moduleName=front.zreport', 'post', params=params)

    def update_shift_employee(self, shift_id, employee_id):
        params = {
            'id': shift_id,
            'openedEmployee': {'id': employee_id},
            'kkmTerminal': {'id': self.places_to_sell.quickresto_kkm_id},
            'closedEmployee': {'id': employee_id},
        }
        return self.send_request('api/update?moduleName=front.zreport', 'post', params=params)

    def close_shift(self, shift_id, employee_id, closed, total_receipts, total_cash, total_card):
        params = {
            'id': shift_id,
            'incomplete': False,
            'status': 'CLOSED',
            'kkmTerminal': {'id': self.places_to_sell.quickresto_kkm_id},
            'closedEmployee': {'id': employee_id},
            'closed': closed.isoformat().replace('+00:00', 'Z'),
            "totalCard": total_card,
            "totalCash": total_cash,
            "ordersCount": total_receipts,

        }
        return self.send_request('api/update?moduleName=front.zreport', 'post', params=params)

    def remove_shift(self, shift_id):
        params = {'id': shift_id, 'className': 'ru.edgex.quickresto.modules.front.zreport.Shift'}
        return self.send_request('api/remove?moduleName=front.zreport', 'post', params=params)

    def create_receipt(self, date_create, general, shift_info, sum_info, dishes):
        params = [
            {"actionType": "create", "moduleName": "front.orders",
             "entity": {"tableOrderCreateTime": date_create.isoformat().replace('+00:00', 'Z'), "documentNumber": sum_info['document_number'],
                        "createDate": date_create.isoformat().replace('+00:00', 'Z'), "returned": False,
                        "frontTotalPrice": sum_info['total_sum'], "frontTotalCashMinusDiscount": sum_info['cash_sum'],
                        "frontTotalCard": sum_info['card_sum'], "cashier": {"id": general['employee_id']},
                        "shiftId": f"{self.places_to_sell.quickresto_place_id}_{shift_info['shift_id']}",
                        "shift": {"id": shift_info['shift_id']}, "kkmTerminal": {"id": self.places_to_sell.quickresto_kkm_id}}}]
        payment = {"actionType": "create", "moduleName": "front.orders.payment",
                   "entity": {"order": {"id": "${1.id}"}, "amount": sum_info['total_sum'],
                              "paymentType": {"id": general['payment_type']}, "customerType": "ORGANIZATION"}}
        process = {"actionType": "action", "moduleName": "warehouse.store.reprocessor", "actionName": "processSince",
                   "entity": {"data": {"since": int(timezone.now().timestamp())}}}
        orders = []
        for dish in dishes:
            order = {"actionType": "create", "moduleName": "front.preorders.preorderitem",
                     "entity": {"order": {"id": "${1.id}"}, "storeItem": {"id": dish['id']}, "amount": dish['amount'],
                     "price": dish['price'], "totalPrice": dish['amount']*dish['price'],
                     "cookingPlace": {"id": self.places_to_sell.quickresto_cookplace_id},
                     "salePlace": {"id": self.places_to_sell.quickresto_place_id}}}
            orders.append(order)
        shift_update = {"actionType": "update", "moduleName": "front.zreport",
                        "entity": {'id': shift_info['shift_id'], 'kkmTerminal': {'id': self.places_to_sell.quickresto_kkm_id},
                        "totalCard": shift_info['total_card'], "totalCash": shift_info['total_cash'],
                        "ordersCount": shift_info['total_receipts']}}

        params.extend(orders)
        params.append(payment)
        params.append(process)
        params.append(shift_update)
        return self.send_request('api/write', 'post', params=params)

    def remove_receipt(self, receipt_id):
        params = {'id': receipt_id, 'className': 'ru.edgex.quickresto.modules.front.orders.OrderInfo'}
        return self.send_request('api/remove?moduleName=front.orders', 'post', params=params)

    def list_all_dish_objects(self, ):
        return self.send_request('api/list?moduleName=warehouse.nomenclature.dish', 'get')

    def tree_all_dish_objects(self, ):
        return self.send_request('api/tree?moduleName=warehouse.nomenclature.dish', 'get')

    def send_request(self, endpoint, method, params=None):
        if method == 'get':
            response = requests.get(self.BASE_URL + endpoint, headers=self.HEADER, json=params,
                                    auth=(self.login, self.password))
        else:
            response = requests.post(self.BASE_URL + endpoint, headers=self.HEADER, json=params,
                                     auth=(self.login, self.password))

        return response
