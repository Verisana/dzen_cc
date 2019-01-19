import json

import telegram
from profiles.models import TelegramBotSettings


class ErrorsHandler():
    def __init__(self):
        self.telegram_sett = TelegramBotSettings.objects.get(name='DzenGroup_bot')
        self.telegram = telegram.Bot(token=self.telegram_sett.token)

    def invalid_response_code(self, file_name, function_name, line_number, response, text=None):
        message = f'Error!\nFunction = {function_name}\nFile = {file_name}\nLine = {line_number}\nResponse code = {response.status_code}\nResponse text = {response.text}\nText = {text}'
        error = json.loads(response.text)

        if error.get('Errors'):
            if not error.get('Errors')[0] == 'InternalError':
                self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)
        else:
            self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)

    def invalid_response_content(self, file_name, function_name, line_number, response, text):
        message = f'Error!\nFunction = {function_name}\nFile = {file_name}\nLine = {line_number}\nResponse text = {response}\nText = {text}'
        self.telegram.send_message(chat_id=self.telegram_sett.chat_emerg, text=message)