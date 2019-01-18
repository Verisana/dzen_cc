import requests
from django.utils import timezone

from profiles.models import QuickRestoApi


class QuickRestoConnector():
    BASE_URL = 'https://td581.quickresto.ru/platform/online/'
    HEADER = {'content-type': 'application/json', 'Connection': 'keep-alive'}

    def __init__(self, setting_id):
        self.quickresto_sett = QuickRestoApi.objects.get(id=setting_id)
        self.login = self.quickresto_sett.api_login
        self.password = self.quickresto_sett.api_pass

    def list_all_shifts(self):
        return self.send_request('api/list?moduleName=front.zreport', 'get')

    def open_shift(self, front_id, kkm_id, shift_number, employee_id, place_id, opened):
        params = {
            'frontId': front_id,
            'incomplete': True,
            'status': 'OPENED',
            'kkmTerminal': {'id': kkm_id},
            'shiftNumber': shift_number,
            'openedEmployee': {'id': employee_id},
            'opened': opened.isoformat().replace('+00:00', 'Z'),
            'salePlace': {'id': place_id},
        }
        return self.send_request('api/create?moduleName=front.zreport', 'post', params=params)

    def close_shift(self, id, kkm_id, employee_id, closed):
        params = {
            'id': id,
            'incomplete': False,
            'status': 'CLOSED',
            'kkmTerminal': {'id': kkm_id},
            'closedEmployee': {'id': employee_id},
            'closed': closed.isoformat().replace('+00:00', 'Z'),
        }
        return self.send_request('api/update?moduleName=front.zreport', 'post', params=params)

    def remove_shift(self, shift_id):
        params = {'id': shift_id, 'className': 'ru.edgex.quickresto.modules.front.zreport.Shift'}
        return self.send_request('api/remove?moduleName=front.zreport', 'post', params=params)

    def create_receipt(self, date_create, total_sum, cash_sum, card_sum, employee_id, shift_front, shift_id, kkm_id,
                       place, payment_type, dishes, shift_info):
        params = [
            {"actionType": "create", "moduleName": "front.orders",
             "entity": {"tableOrderCreateTime": date_create, "createDate": date_create, "returned": False,
                        "frontTotalPrice": total_sum, "frontTotalCashMinusDiscount": cash_sum,
                        "frontTotalCard": card_sum, "cashier": {"id": employee_id}, "shiftId": shift_front,
                        "shift": {"id": shift_id}, "kkmTerminal": {"id": kkm_id}}}]
        payment = {"actionType": "create", "moduleName": "front.orders.payment",
                   "entity": {"order": {"id": "${1.id}"}, "amount": total_sum, "paymentType": {"id": payment_type},
                              "customerType": "ORGANIZATION"}}
        process = {"actionType": "action", "moduleName": "warehouse.store.reprocessor", "actionName": "processSince",
                   "entity": {"data": {"since": int(timezone.now().timestamp())}}}
        orders = []
        for dish in dishes:
            order = {"actionType": "create", "moduleName": "front.preorders.preorderitem",
                     "entity": {"order": {"id": "${1.id}"}, "storeItem": {"id": dish['id']}, "amount": dish['amount'],
                     "price": dish['price'], "totalPrice": dish['amount']*dish['price'],
                     "cookingPlace": {"id": place[1]}, "salePlace": {"id": place[0]}}}
            orders.append(order)
        shift_update = {"actionType": "update", "moduleName": "front.zreport",
                        "entity": {'id': shift_id, 'kkmTerminal': {'id': kkm_id}, 'closedEmployee': {'id': employee_id},
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
