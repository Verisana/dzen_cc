import json
from datetime import timedelta
from inspect import currentframe, getframeinfo
from utils.errors_handler import ErrorsHandler
from dateutil.parser import parse
from django.utils import timezone
from profiles.models import OfdruApi
from data_sync_bot.models import SalesData, PlacesToSell, EmployeesList, GoodsToSale, GoodsBase
from data_sync_bot.api_manager.ofdru_api import OFDruConnector


class OFDReceiptSaver():
    def __init__(self):
        self.errors = ErrorsHandler()
        self.ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
        self.places_to_sell = PlacesToSell.objects.all()
        self.employees_list = EmployeesList.objects.all()
        self.goods_base = GoodsBase.objects.all()

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


    def fillup_salesdata_entry(self, receipt, new_salesdata_object):
        if receipt['Data']['Amount_Cash']:
            payment_type = 'cash'
        else:
            payment_type = 'electronic'

        staff_name = None
        for employee in self.employees_list:
            if employee.mask_ident.lower() in receipt['Data']['Operator'].lower():
                staff_name = employee
                break

        sold_goods = []
        recognized_goods = []
        for item in receipt['Data']['Items']:
            for goods in self.goods_base:
                if goods.keyword_ident.lower() in item['Name'].lower():
                    recognized_goods.append([goods, int(item['Quantity'])])
                    break

        for index, goods in enumerate(recognized_goods):
            for index2, i in enumerate(recognized_goods):
                if goods[0].id == i[0].id and index != index2:
                    goods[1] += i[1]
                    recognized_goods.remove(i)

        if recognized_goods:
            for goods in recognized_goods:
                new_item = GoodsToSale.objects.get_or_create(
                    goods_object=goods[0],
                    amount=goods[1],
                )
                sold_goods.append(new_item[0])
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno, receipt['Data']['Items'])

        if payment_type and sold_goods and staff_name:
            is_fulled = True
        else:
            is_fulled = False

        new_salesdata_object.sold_goods.set(sold_goods)
        new_salesdata_object.is_fulled = is_fulled
        new_salesdata_object.payment_type = payment_type
        new_salesdata_object.staff_name = staff_name
        new_salesdata_object.save()

    def create_new_entry_salesdata(self, receipt):
        is_fulled, receipt_sum = True, None
        if receipt['Data']['Tag'] == 3:
            receipt_type = 'sale'
            receipt_sum = receipt['Data']['Amount_Total'] / 100
            is_fulled = False
        elif receipt['Data']['Tag'] == 2:
            receipt_type = 'open_shift'
        else:
            receipt_type = 'close_shift'

        address = None
        for place in self.places_to_sell:
            if place.kkt_number in receipt['Data']['KKT_RegNumber']:
                address = place
                break

        new_salesdata_object = SalesData.objects.create(
                shift_number=receipt['Data']['ShiftNumber'],
                receipt_num=receipt['Data']['Document_Number'],
                receipt_num_inshift=receipt['Data']['Number'],
                deal_date=parse(receipt['Data']['DateTime']).astimezone(),
                kkt_rnm=receipt['Data']['KKT_RegNumber'],
                fnnum=receipt['Data']['FN_FactoryNumber'],
                address=address,
                is_fulled=is_fulled,
                receipt_type=receipt_type,
                receipt_sum=receipt_sum,
            )

        if receipt['Data']['Tag'] == 3:
            self.fillup_salesdata_entry(receipt, new_salesdata_object)

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