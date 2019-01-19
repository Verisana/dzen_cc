import json
from decimal import *
from datetime import timedelta
from inspect import currentframe, getframeinfo

from dateutil.parser import parse
from django.utils import timezone

from data_sync_bot.api_manager.quickresto_api import QuickRestoConnector
from data_sync_bot.models import SalesData, PlacesToSell, EmployeesList, GoodsToSale, GoodsBase
from profiles.models import QuickRestoApi
from utils.errors_handler import ErrorsHandler


class QuickRestoSaver:
    def __init__(self):
        self.errors = ErrorsHandler()
        self.ofdru_sett = QuickRestoApi.objects.get(name='QuickResto_Dzen')
        self.places_to_sell = PlacesToSell.objects.all()
        self.employees_list = EmployeesList.objects.all()
        self.goods_base = GoodsBase.objects.all()

    def open_shift(self, receipt, quickresto_conn):
        if receipt.staff_name:
            staff_name = receipt.staff_name.quickresto_id
        else:
            staff_name = None
        response = quickresto_conn.open_shift(receipt.shift_number, staff_name,
                                              receipt.deal_date)
        if response.status_code == 200:
            response = json.loads(response.text)
            receipt.quickresto_shift_id = response['id']
            receipt.is_uploaded_quickresto = True
            receipt.save()
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno,
                                              response)

    def close_shift(self, receipt, quickresto_conn):
        if receipt.staff_name:
            staff_name = receipt.staff_name.quickresto_id
        else:
            staff_name = None
        shift_id = SalesData.objects.get(address=receipt.address, shift_number=receipt.shift_number,
                                         receipt_num_inshift=0).quickresto_shift_id
        response = quickresto_conn.close_shift(shift_id, staff_name, receipt.deal_date)
        if response.status_code == 200:
            receipt.is_uploaded_quickresto = True
            receipt.save()
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno,
                                              response)

    def count_shift_sums(self, place, shift_number, last_receipt):
        receipts = SalesData.objects.filter(address=place,shift_number=shift_number, receipt_type='sale',
                                            receipt_num_inshift__lte=last_receipt).order_by('receipt_num_inshift')
        total_receipts = 0
        total_cash = Decimal('0.0')
        total_card = Decimal('0.0')
        for receipt in receipts:
            total_receipts += 1
            if receipt.payment_type == 'cash':
                total_cash += receipt.receipt_sum
            else:
                total_card += receipt.receipt_sum
        return total_receipts, total_cash, total_card

    def create_receipt(self, receipt, quickresto_conn):
        if receipt.staff_name:
            staff_name = receipt.staff_name.quickresto_id
        else:
            staff_name = None

        if receipt.payment_type == 'cash':
            cash_sum = float(round(receipt.receipt_sum, 2))
            card_sum = 0.0
            payment_type = 1
        else:
            cash_sum = 0.0
            card_sum = float(round(receipt.receipt_sum, 2))
            payment_type = 2

        general = {
            'employee_id': staff_name,
            'payment_type': payment_type,
        }

        total_receipts, total_cash, total_card = self.count_shift_sums(receipt.address, receipt.shift_number, receipt.receipt_num_inshift)
        shift_id = SalesData.objects.get(address=receipt.address, shift_number=receipt.shift_number, receipt_num_inshift=0).quickresto_shift_id
        shift_info = {
            'shift_id': shift_id,
            'total_card': float(round(total_card, 2)),
            'total_cash': float(round(total_cash, 2)),
            'total_receipts': total_receipts,
        }

        sum_info = {
            'total_sum': float(round(receipt.receipt_sum, 2)),
            'card_sum': float(round(cash_sum, 2)),
            'cash_sum': float(round(card_sum, 2)),
        }

        dishes = []
        if receipt.sold_goods.all():
            for dish in receipt.sold_goods.all():
                sold = {
                    'id': dish.goods_object.quickresto_id,
                    'amount': dish.amount,
                    'price': float(round(dish.goods_object.base_price.get(place_to_sale=receipt.address).price, 2)),
                }
                dishes.append(sold)
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            text = 'В чеке нет информации по проданным позициям'
            self.errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno,
                                                 receipt.id, text)


        response = quickresto_conn.create_receipt(receipt.deal_date, general, shift_info, sum_info, dishes)
        if response.status_code == 200:
            receipt.is_uploaded_quickresto = True
            receipt.save()
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            self.errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno,
                                              response)

    def update_quikresto(self):
        for place in self.places_to_sell:
            quickresto_conn = QuickRestoConnector(setting_id=1, place_id=place.id)
            unsaved_receipts = SalesData.objects.filter(address=place, is_uploaded_quickresto=False).order_by('deal_date')
            for receipt in unsaved_receipts:
                if receipt.receipt_type == 'open_shift':
                    self.open_shift(receipt, quickresto_conn)
                elif receipt.receipt_type == 'close_shift':
                    self.close_shift(receipt, quickresto_conn)
                else:
                    self.create_receipt(receipt, quickresto_conn)