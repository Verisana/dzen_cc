from celery import shared_task
from data_sync_bot.receipt_manager.ofd_receipt_saver import OFDReceiptSaver
from data_sync_bot.receipt_manager.quickresto_saver import QuickRestoSaver


@shared_task
def check_updates():
    ofdru_saver = OFDReceiptSaver()
    ofdru_saver.check_new_receipts()
    qr_saver = QuickRestoSaver()
    qr_saver.update_quikresto()