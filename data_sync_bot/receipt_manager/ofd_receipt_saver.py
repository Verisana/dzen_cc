import json
from datetime import timedelta
from inspect import currentframe, getframeinfo
from utils.errors_handler import ErrorsHandler
from dateutil.parser import parse
from django.utils import timezone
from profiles.models import OfdruApi
from data_sync_bot.models import SalesData, PlacesToSell, EmployeesList, GoodsToSale, GoodsBase
from data_sync_bot.api_manager.ofdru_api import OFDruConnector


class OFDReceiptSaver:
    def __init__(self):
        self.errors = ErrorsHandler()
        self.ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
        self.places_to_sell = PlacesToSell.objects.all()
        self.employees_list = EmployeesList.objects.all()
        self.goods_base = GoodsBase.objects.all()

    def check_response_for_errors(self, response, text, debug_info=None):
        if not debug_info:
            debug_info = {
                'filename': None,
                'function_name': None,
                'line_number': None,
            }

        if response.status_code == 200:
            response = json.loads(response.text)
            if not response['Status'] == 'Success':
                self.errors.invalid_response_content(debug_info['filename'],
                                                     debug_info['function_name'],
                                                     debug_info['line_number'],
                                                     response, text)
                return False
            return response
        else:
            self.errors.invalid_response_code(debug_info['filename'],
                                              debug_info['function_name'],
                                              debug_info['line_number'],
                                              response, text)
            return False

    def get_receipts_bydate(self, date_from, date_to, ofdru_conn):
        text = [date_from, date_to]
        receipts_by_date = ofdru_conn.get_daterange_receipts(date_from, date_to)
        cf = currentframe()
        filename = getframeinfo(cf).filename
        debug_info = {
            'filename': filename,
            'function_name': cf.f_code.co_name,
            'line_number': cf.f_lineno,
        }
        return self.check_response_for_errors(receipts_by_date, text, debug_info=debug_info)

    def get_receipt_by_num(self, shift_num, receipt_num, ofdru_conn):
        text = [shift_num, receipt_num, ofdru_conn.places_to_sell.address]
        receipt_info = ofdru_conn.get_recepit_info_bynum(shift_num=shift_num,
                                                         receipt_num=receipt_num)
        cf = currentframe()
        filename = getframeinfo(cf).filename
        debug_info = {
            'filename': filename,
            'function_name': cf.f_code.co_name,
            'line_number': cf.f_lineno,
        }
        return self.check_response_for_errors(receipt_info, text, debug_info=debug_info)

    def get_closedshift_receipts(self, shift_num, ofdru_conn):
        text = [shift_num, ofdru_conn.places_to_sell.address]
        receipt_info = ofdru_conn.get_closedshift_receipts(shift_num)
        cf = currentframe()
        filename = getframeinfo(cf).filename
        debug_info = {
            'filename': filename,
            'function_name': cf.f_code.co_name,
            'line_number': cf.f_lineno,
        }
        return self.check_response_for_errors(receipt_info, text, debug_info=debug_info)

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
            text = 'No recognized goods'
            self.errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno, receipt['Data']['Items'], text)

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
            receipt_num_inshift = receipt['Data']['Number']
        elif receipt['Data']['Tag'] == 2:
            receipt_type = 'open_shift'
            receipt_num_inshift = 0
        else:
            receipt_type = 'close_shift'
            last_receipt = SalesData.objects.filter(shift_number=receipt['Data']['ShiftNumber']).order_by('-receipt_num_inshift')[0]
            receipt_num_inshift = last_receipt.receipt_num_inshift + 1

        address = None
        for place in self.places_to_sell:
            if place.kkt_number in receipt['Data']['KKT_RegNumber']:
                address = place
                break

        new_salesdata_object = SalesData.objects.update_or_create(
            kkt_rnm=receipt['Data']['KKT_RegNumber'],
            receipt_num=receipt['Data']['Document_Number'],
            defaults = {
                'shift_number': receipt['Data']['ShiftNumber'],
                'receipt_num_inshift': receipt_num_inshift,
                'deal_date': parse(receipt['Data']['DateTime']).astimezone(),
                'fnnum': receipt['Data']['FN_FactoryNumber'],
                'address': address,
                'is_fulled': is_fulled,
                'receipt_type': receipt_type,
                'receipt_sum': receipt_sum,
            }
        )

        if receipt['Data']['Tag'] == 3:
            self.fillup_salesdata_entry(receipt, new_salesdata_object[0])

    def check_open_shift_receipt(self, shift_number, ofdru_conn, place):
        try:
            SalesData.objects.filter(address=place).get(shift_number=shift_number, receipt_num_inshift=0)
        except SalesData.DoesNotExist:
            open_receipt = self.get_receipt_by_num(shift_num=shift_number,
                                                   receipt_num=0,
                                                   ofdru_conn=ofdru_conn)
            self.create_new_entry_salesdata(open_receipt)

    def check_close_shift_receipt(self, shift_number, ofdru_conn, place):
        try:
            SalesData.objects.filter(address=place).get(shift_number=shift_number, receipt_type='close_shift')
        except SalesData.DoesNotExist:
            if SalesData.objects.filter(address=place).filter(shift_number=shift_number).order_by('-receipt_num_inshift'):
                last_receipt_inshift = SalesData.objects.filter(address=place).filter(shift_number=shift_number).order_by('-receipt_num_inshift')[0]
                close_receipt = self.get_receipt_by_num(shift_num=shift_number,
                                                        receipt_num=last_receipt_inshift.receipt_num_inshift+1,
                                                        ofdru_conn=ofdru_conn)
                self.create_new_entry_salesdata(close_receipt)
            else:
                pass

    def add_new_receipts(self, receipts_to_add, ofdru_conn, place):
        for receipt in receipts_to_add['Data'][::-1]:
            try:
                last_receipt = SalesData.objects.filter(address=place).latest('deal_date')
            except SalesData.DoesNotExist:
                self.check_open_shift_receipt(receipt['DocShiftNumber'], ofdru_conn, place)
                receipt_info = self.get_receipt_by_num(shift_num=receipt['DocShiftNumber'],
                                                       receipt_num=receipt['ReceiptNumber'],
                                                       ofdru_conn=ofdru_conn)
                self.create_new_entry_salesdata(receipt_info)
                last_receipt = SalesData.objects.filter(address=place).latest('deal_date')

            if receipt['ReceiptNumber'] == 1:
                self.check_open_shift_receipt(receipt['DocShiftNumber'], ofdru_conn, place)
                self.check_close_shift_receipt(receipt['DocShiftNumber']-1, ofdru_conn, place)

            if receipt['DocNumber'] > last_receipt.receipt_num:
                receipt_info = self.get_receipt_by_num(shift_num=receipt['DocShiftNumber'],
                                                       receipt_num=receipt['ReceiptNumber'],
                                                       ofdru_conn=ofdru_conn)
                self.create_new_entry_salesdata(receipt_info)

    def check_integrity(self, ofdru_conn):
        empty_receipts = SalesData.objects.filter(sold_goods=None, receipt_type='sale')
        if not empty_receipts:
            for receipt in empty_receipts:
                receipt_from_ofd = self.get_receipt_by_num(receipt.shift_number, receipt.receipt_num_inshift, ofdru_conn)
                self.fillup_salesdata_entry(receipt_from_ofd, receipt)

        sales_data_to_check = SalesData.objects.filter(kkt_rnm=ofdru_conn.places_to_sell.kkt_number,
                                                       deal_date__range=(timezone.now().astimezone()-timezone.timedelta(days=1),
                                                                         timezone.now().astimezone())
                                                       )
        if not sales_data_to_check:
            for counter, data in enumerate(sales_data_to_check):
                if counter > 0:
                    if not data.receipt_num-1 == sales_data_to_check[counter-1].receipt_num:
                        cf = currentframe()
                        filename = getframeinfo(cf).filename
                        text = f'Missed receipt: {data.receipt_num-1} != {sales_data_to_check[counter-1].receipt_num}'
                        self.errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno,
                                                             data, text)

    def check_new_receipts(self):
        for place in self.places_to_sell:
            ofdru_conn = OFDruConnector(setting_id=self.ofdru_sett.id, place_id=place.id)
            now_time = timezone.now().astimezone()
            time_diff = now_time - timedelta(minutes=5)
            receipts_by_date = self.get_receipts_bydate(time_diff.strftime('%Y-%m-%dT%H:%M'),
                                                       now_time.strftime('%Y-%m-%dT%H:%M'),
                                                       ofdru_conn)
            self.check_integrity(ofdru_conn)
            if receipts_by_date != False:
                self.add_new_receipts(receipts_by_date, ofdru_conn, place)