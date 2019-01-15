import telegram
from profiles.models import TelegramBotSettings


class ErrorsHandler():
    def __init__(self):
        self.telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
        pp = telegram.utils.request.Request(proxy_url='https://10.0.2.2:1080')
        self.telegram = telegram.Bot(token=self.telegram_sett.token, request=pp)

    def invalid_response_code(self, file_name, function_name, line_number, response, text):
        message = f'Error!\nFunction = {function_name}\nFile = {file_name}\nLine = {line_number}\nResponse code = {response.status_code}\nResponse text = {response.text}\nText = {text}'
        self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)

    def invalid_response_content(self, file_name, function_name, line_number, response, text):
        message = f'Error!\nFunction = {function_name}\nFile = {file_name}\nLine = {line_number}\nResponse text = {response}\nText = {text}'
        self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)