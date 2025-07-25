from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import string
import random

class Profile(models.Model):
    """
    Расширенный профиль пользователя.

    Связь:
    - Один-к-одному с моделью User.

    Поля:
    - phone_number: уникальный номер телефона.
    - invite_code: уникальный инвайт-код (может быть пустым).
    - activated_invite: ссылка на профиль, чей код был активирован этим пользователем.

    Методы:
    - generate_invite_code: генерирует уникальный 6-символьный инвайт-код (латиница + цифры).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(unique=True)
    invite_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    activated_invite = models.ForeignKey('self', null=True, blank=True, default=None, on_delete=models.SET_NULL)

    def generate_invite_code(self):
        """
        Генерирует и устанавливает уникальный 6-символьный инвайт-код.
        """
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            if not Profile.objects.filter(invite_code=code).exists():
                self.invite_code = code
                break
    
class PhoneOnlyLoginCode(models.Model):
    """
    Одноразовый код для входа по номеру телефона без пароля.

    Связь:
    - Один-к-одному с Profile.

    Поля:
    - code: 4-значный одноразовый код.
    - created_at: время создания кода.
    - TTL_MINUTES: время жизни кода (по умолчанию 5 минут).

    Методы:
    - is_expired(): возвращает True, если код устарел.
    """
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    TTL_MINUTES = 5 

    def is_expired(self):
        """
        Проверяет, истёк ли срок действия кода.

        Возвращает:
        - True, если код старше 5 минут.
        """
        return timezone.now() > self.created_at + timedelta(minutes=self.TTL_MINUTES)

    def __str__(self):
        return f"{self.profile.phone_number} - {self.code}"