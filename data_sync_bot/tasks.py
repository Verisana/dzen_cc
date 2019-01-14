from celery import shared_task
from data_sync_bot.receipt_manager.ofd_receipt_saver import OFDReceiptSaver


@shared_task
def check_updates():
    ofdru_saver = OFDReceiptSaver()
    ofdru_saver.check_new_receipts()