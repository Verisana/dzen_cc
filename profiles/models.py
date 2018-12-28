from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    pass


class QuickRestoApi(models.Model):
    name = models.CharField(max_length=64)
    api_login = models.CharField(max_length=32)
    api_pass = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.name}'


class OfdruApi(models.Model):
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    login = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return f'{self.name}'


class KonturOfdApi(models.Model):
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.name}'


class TelegramBotSettings(models.Model):
    name = models.CharField(max_length=64)
    token = models.CharField(max_length=64)
    chat_emerg = models.CharField(max_length=32, blank=True, null=True)
    chat_info = models.CharField(max_length=32, blank=True, null=True)
    proxy = models.CharField(max_length=25, blank=True, null=True)
    def __str__(self):
        return f'{self.name}'