import json
from datetime import timedelta
from inspect import currentframe, getframeinfo
from utils.errors_handler import ErrorsHandler
from celery import shared_task
from django.utils import timezone
from profiles.models import OfdruApi
from data_sync_bot.models import SalesData, PlacesToSell
from data_sync_bot.api_manager.ofdru_api import OFDruConnector


@shared_task
def add_new_receipts(receipts_to_add):
    try:
        last_receipt = SalesData.objects.latest('deal_date')
    except SalesData.DoesNotExist:
        last_receipt = None
        for receipt in receipts_to_add['Data']:



@shared_task
def check_new_receipts():
    errors = ErrorsHandler()
    ofdru_sett = OfdruApi.objects.get(name='OFDru_Dzen')
    places_to_sell = PlacesToSell.objects.all()

    for kkts in places_to_sell:
        ofdru_conn = OFDruConnector(setting_id=ofdru_sett.id, infokkt_id=kkts.id)
        now_time = timezone.now().astimezone()
        time_diff = now_time - timedelta(minutes=10)
        receipts_by_date = ofdru_conn.get_daterange_receipts(time_diff.strftime('%Y-%m-%dT%H:%M'),
                                                             now_time.strftime('%Y-%m-%dT%H:%M'))
        if  receipts_by_date.status_code == 200:
            receipts_by_date = json.loads(receipts_by_date.text)
            if not receipts_by_date['Status'] == 'Success':
                cf = currentframe()
                filename = getframeinfo(cf).filename
                errors.invalid_response_content(filename, cf.f_code.co_name, cf.f_lineno, receipts_by_date)
                return False
            add_new_receipts(receipts_by_date)
        else:
            cf = currentframe()
            filename = getframeinfo(cf).filename
            errors.invalid_response_code(filename, cf.f_code.co_name, cf.f_lineno, receipts_by_date)
            return False