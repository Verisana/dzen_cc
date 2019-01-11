import json
from datetime import timedelta
from inspect import currentframe, getframeinfo
from utils.errors_handler import ErrorsHandler
from celery import shared_task
from django.utils import timezone
from profiles.models import OfdruApi
from data_sync_bot.models import SalesData, PlacesToSell
from data_sync_bot.api_manager.ofdru_api import OFDruConnector


class OFDReceiptSaver():
    def __init__(self):
        self.errors = ErrorsHandler()
        self.ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
        self.places_to_sell = PlacesToSell.objects.all()

    def check_response_for_errors(self, response):
        if response.status_code == 200:
            response = json.loads(response.text)
            if not response['Status'] == 'Success':
                cf = currentframe()
                filename = getframeinfo(cf).filename
                self.errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno, response)
                return False
            return response
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno, response)
            return False

    def get_receipts_bydate(self, date_from, date_to, ofdru_conn):
        receipts_by_date = ofdru_conn.get_daterange_receipts(date_from, date_to)
        return self.check_response_for_errors(receipts_by_date)

    def get_receipt_by_num(self, shift_num, receipt_num, ofdru_conn):
        receipt_info = ofdru_conn.get_recepit_info_bynum(shift_num=shift_num,
                                                         receipt_num=receipt_num)
        return self.check_response_for_errors(receipt_info)

    def create_new_entry_salesdata(self, receipt):
        if receipt['Data']['Tag'] == 3:
            receipt_type = 'sale'
        elif receipt['Data']['Tag'] == 2:
            receipt_type = 'open_shift'
        else:
            receipt_type = 'close_shift'

        SalesData.objects.create(
            shift_number=receipt['Data'][''],
            receipt_num=receipt['Data'][''],
            receipt_num_inshift=receipt['Data'][''],
            deal_date=receipt['Data'][''],
            kkt_rnm=receipt['Data'][''],
            fnnum=receipt['Data'][''],
            address=,
            receipt_type=,
            is_fulled=True,
            sold_goods=,
            staff_name=,
            payment_type=,
            receipt_sum=receipt['Data']['Amount_Total'] / 100,
        )

    def add_new_receipts(self, receipts_to_add, ofdru_conn):
        try:
            last_receipt = SalesData.objects.latest('deal_date')
        except SalesData.DoesNotExist:
            last_receipt = None

        for receipt in receipts_to_add['Data']:
            receipt_info = self.get_receipt_by_num(shift_num=receipt['DocShiftNumber'],
                                                   receipt_num=receipt['ReceiptNumber'],
                                                   ofdru_conn=ofdru_conn)

    def check_new_receipts(self):
        for place in self.places_to_sell:
            ofdru_conn = OFDruConnector(setting_id=self.ofdru_sett.id, place_id=place.id)
            now_time = timezone.now().astimezone()
            time_diff = now_time - timedelta(minutes=10)
            receipts_by_date = self.get_receipts_bydate(time_diff.strftime('%Y-%m-%dT%H:%M'),
                                                       now_time.strftime('%Y-%m-%dT%H:%M'),
                                                       ofdru_conn)
            if receipts_by_date != False:
                self.add_new_receipts(receipts_by_date, ofdru_conn)