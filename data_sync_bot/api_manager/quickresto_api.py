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

    def open_shift(self, front_id, kkm_id, shift_number, employee_id, opened):
        params = {
            'frontId': front_id,
            'incomplete': True,
            'status': 'OPENED',
            'kkmTerminal': {'id': kkm_id},
            'shiftNumber': shift_number,
            'openedEmployee': {'id': employee_id},
            'opened': opened.isoformat().replace('+00:00', 'Z'),
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

    def create_receipt(self):
        params = {
            'cashier': {'id': 4},
            'returned': False,
            'createDate': timezone.now().isoformat().replace('+00:00', 'Z'),
            'documentNumber': 233,
            'kkmTerminalName': {'id': 1},
            'orderItemList': [{"storeItem": {"id": 46}, "amount": 1.0, "cookingPlace": {"id": 1}, "salePlace": {"id": 1}}],
            #'payments': 0,
            'shift': {'id': 17},
        }
        params = [
            {"actionType": "create", "moduleName": "front.orders",
             "entity": {"tableOrderCreateTime":"2017-07-21T08:00:00.000Z", "createDate":"2017-07-21T08:01:00.000Z", "returned": False,
                        "table": {"id": 1}, "cashier": {"id": 1}, "waiter": {"id": 1}, "frontTotalPrice": 99.0, "frontTotalAbsoluteDiscount": 3.0,
                        "frontTotalAbsoluteCharge": 2.0, "frontSum": 100.0, "frontTotalCashMinusDiscount": 50.0, "frontTotalCard": 40.0,
                        "frontTotalBonuses": 9.0, "shiftId":"dr-shift-1", "shift":{"id": shift_id, "kkmTerminal": {"id": 1}}
                },
            {"actionType": "create", "moduleName": "front.preorders.preorderitem",
             "entity": {"order": {"id": "${1.id}"}, "storeItem": {"id": 1}, "amount": 2.0, "price": 50.0, "totalPrice": 100.0, "totalAbsoluteDiscount": 3.0,
                        "totalAbsoluteCharge": 2.0, "cookingPlace": {"id": 1}, "salePlace": {"id": 1}}
                },
            {"actionType": "create", "moduleName": "front.orders.payment",
             "entity": {"order":{"id": "${1.id}"}, "amount": 50.0, "paymentType": {"id": 1}, "customerType": "ORGANIZATION"}
                },
            {"actionType": "create", "moduleName": "front.orders.cashlessorder",
             "entity": {"owner": {"id": "${1.id}"}, "pos": {"id": 2}, "totalSum": 40.0}
             },
            {"actionType": "action", "moduleName": "warehouse.store.reprocessor", "actionName": "processSince",
             "entity": {"data" : {"since": 1500624000000}}
             },
        ]
        return self.send_request('api/create?moduleName=front.orders', 'post', params=params)

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
