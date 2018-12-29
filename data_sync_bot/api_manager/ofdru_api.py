import requests
import json
from django.utils import timezone
from dateutil.parser import parse
from profiles.models import OfdruApi, TelegramBotSettings, InfoKKT
import telegram


class OFDruConnector():
    BASE_URL = 'https://ofd.ru'
    HEADER = {'content-type': 'application/json', 'charset': 'utf-8'}

    def __init__(self, setting_id, infokkt_id):
        self.ofdru_sett = OfdruApi.objects.get(id=setting_id)
        self.infokkt = InfoKKT.objects.get(id=infokkt_id)
        self.inn = self.infokkt.ip_inn
        self.kkt = self.infokkt.kkt_number
        self.fnnum = self.infokkt.fn_number
        self.telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
        self.login = self.ofdru_sett.login
        self.password = self.ofdru_sett.password
        if not self.ofdru_sett.token_expiration or not self.ofdru_sett.token:
            self.get_new_token()
        else:
            if timezone.now().timestamp() >= self.ofdru_sett.token_expiration.timestamp():
                self.get_new_token()
        self.token = self.ofdru_sett.token
        self.telegram = telegram.Bot(token=self.telegram_sett.token)

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
            message = f'Error in function "get_new_token"/nResponse code: {response.status_code}/nResponse text: {response.text}'
            self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)
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