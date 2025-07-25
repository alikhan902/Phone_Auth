from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile.

    Представляет основные поля профиля пользователя, в данном случае:
    - phone_number: номер телефона пользователя.
    """
    class Meta:
        model = Profile
        fields = ['phone_number']


class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    """
    Сериализатор для модели User вместе с вложенным ProfileSerializer.

    Поля:
    - username: имя пользователя.
    - password: пароль (write-only).
    - profile: данные профиля (вложенный сериализатор ProfileSerializer).

    Методы:
    - create: создаёт пользователя с профилем на основе переданных данных.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Создаёт нового пользователя и связанный профиль.

        Аргументы:
        - validated_data: валидированные данные, включающие данные пользователя и профиля.

        Возвращает:
        - созданный объект User.
        """
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user
