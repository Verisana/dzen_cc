import requests
import json
from django.utils import timezone
from dateutil.parser import parse
from profiles.models import OfdruApi
from data_sync_bot.models import PlacesToSell
from inspect import currentframe, getframeinfo
from utils.errors_handler import ErrorsHandler


class OFDruConnector():
    BASE_URL = 'https://ofd.ru'
    HEADER = {'content-type': 'application/json', 'charset': 'utf-8'}

    def __init__(self, setting_id, place_id):
        self.ofdru_sett = OfdruApi.objects.get(id=setting_id)
        self.places_to_sell = PlacesToSell.objects.get(id=place_id)
        self.inn = self.places_to_sell.ip_inn
        self.kkt = self.places_to_sell.kkt_number
        self.fnnum = self.places_to_sell.fn_number
        self.errors = ErrorsHandler()
        self.login = self.ofdru_sett.login
        self.password = self.ofdru_sett.password
        if not self.ofdru_sett.token_expiration or not self.ofdru_sett.token:
            self.get_new_token()
        else:
            if timezone.now().timestamp() >= self.ofdru_sett.token_expiration.timestamp():
                self.get_new_token()
        self.token = self.ofdru_sett.token

    def get_new_token(self):
        params = {'Login': self.login, 'Password': self.password}
        response = self.send_request('/api/Authorization/CreateAuthToken', 'post', params=params)
        if response.status_code == 200:
            response = json.loads(response.text)
            aware_datetime = parse(response['ExpirationDateUtc'], tzinfos={'tzname': timezone.get_default_timezone_name()})
            self.ofdru_sett.token, self.ofdru_sett.token_expiration = response['AuthToken'], aware_datetime.astimezone()
            self.ofdru_sett.save()
            return True
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno, response)
            return False

    def get_daterange_receipts(self, date_from, date_to):
        '''Date should be string in 2018-12-19T00:00 format'''
        endpoint = f'/api/integration/v1/inn/{self.inn}/kkt/{self.kkt}/receipts?AuthToken={self.token}&dateFrom={date_from}&dateTo={date_to}'
        return self.send_request(endpoint, 'get')

    def get_recepit_info_byid(self, receipt_id):
        endpoint = f'/api/integration/v1/inn/{self.inn}/kkt/{self.kkt}/receipt/{receipt_id}?AuthToken={self.token}'
        return self.send_request(endpoint, 'get')

    def get_recepit_info_bynum(self, shift_num, receipt_num):
        endpoint = f'/api/integration/v1/inn/{self.inn}/kkt/{self.kkt}/zreport/{shift_num}/receipt/{receipt_num}?AuthToken={self.token}'
        return self.send_request(endpoint, 'get')

    def get_closedshift_receipts(self, shift):
        endpoint = f'/api/integration/v1/inn/{self.inn}/kkt/{self.kkt}/receipts?AuthToken={self.token}&ShiftNumber={shift}&FnNumber={self.fnnum}'
        return self.send_request(endpoint, 'get')

    def send_request(self, endpoint, method, params=None):
        if method == 'get':
            response = requests.get(self.BASE_URL+endpoint, headers=self.HEADER, json=params)
        else:
            response = requests.post(self.BASE_URL+endpoint, headers=self.HEADER, json=params)
        return response