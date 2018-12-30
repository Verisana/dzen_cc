import requests
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

    def create_new_shift(self):
        params = {'frontId': 'dr-shift-1'}
        return self.send_request('api/create?moduleName=front.zreport', 'post', params=params)

    def remove_shift(self, shift_id):
        params = {'id': shift_id, 'className': 'ru.edgex.quickresto.modules.front.zreport.Shift'}
        return self.send_request('api/remove?moduleName=front.zreport', 'post', params=params)

    def list_all_dish_objects(self, ):
        return self.send_request('api/list?moduleName=warehouse.nomenclature.dish', 'get')

    def tree_all_dish_objects(self, ):
        return self.send_request('api/tree?moduleName=warehouse.nomenclature.dish', 'get')

    def send_request(self, endpoint, method, params=None):
        if method == 'get':
            response = requests.get(self.BASE_URL+endpoint, headers=self.HEADER, json=params, auth=(self.login, self.password))
        else:
            response = requests.post(self.BASE_URL+endpoint, headers=self.HEADER, json=params, auth=(self.login, self.password))

        return response