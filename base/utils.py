import time
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import PhoneOnlyLoginCode


def generate_otp(profile):
    """
    Генерирует одноразовый код подтверждения (OTP) для указанного профиля.

    Функция создаёт или обновляет объект PhoneOnlyLoginCode, связанный с профилем,
    устанавливая новый 4-значный цифровой код и текущее время создания.

    Задержка в 2 секунды имитирует задержку отправки кода.

    Аргументы:
    - profile (Profile): профиль пользователя, для которого генерируется код.

    Возвращает:
    - str: сгенерированный 4-значный код.
    """
    time.sleep(2)
    code = get_random_string(length=4, allowed_chars='0123456789')
    PhoneOnlyLoginCode.objects.update_or_create(
        profile=profile,
        defaults={'code': code, 'created_at': timezone.now()}
    )
    return code