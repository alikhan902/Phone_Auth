from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from .permissions import IsNotAuthenticated
from .models import PhoneOnlyLoginCode, Profile
from .utils import generate_otp
from .serializer import ProfileSerializer, UserWithProfileSerializer
from rest_framework import generics
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated

class UserWithProfileViewSet(generics.CreateAPIView):
    """
    Регистрация пользователя с привязанным профилем.
    
    Доступ: только неавторизованные пользователи.
    """
    queryset = User.objects.all()
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsNotAuthenticated]
    
    
class SendCodeView(APIView):
    """
    Отправка одноразового кода (OTP) на указанный номер телефона.

    Доступ: только неавторизованные пользователи.

    Параметры:
    - phone_number (str): номер телефона зарегистрированного пользователя.
    
    Ответ:
    - detail (str): статус операции.
    - code (str): сгенерированный код (только в dev-режиме, в реальности будет отправляться по SMS).
    """
    
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        phone = request.data.get('phone_number')
        if not phone:
            return Response({'detail': 'Phone number is required'}, status=400)

        try:
            profile = Profile.objects.get(phone_number=phone)
        except Profile.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)

        code = generate_otp(profile)

        return Response({'detail': 'Code sent', 'code': code}) 


class VerifyCodeView(APIView):
    """
    Подтверждение кода и вход в систему.

    Доступ: только неавторизованные пользователи.

    Параметры:
    - phone_number (str): номер телефона.
    - code (str): одноразовый код, полученный через SendCodeView.
    
    Ответ:
    - detail (str): статус авторизации.
    - username (str): имя пользователя.
    - invite_code (str): собственный инвайт-код пользователя.
    """
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('code')

        if not phone or not code:
            return Response({'detail': 'Phone number and code are required'}, status=400)

        try:
            code_obj = PhoneOnlyLoginCode.objects.select_related('profile').get(profile__phone_number=phone)
        except PhoneOnlyLoginCode.DoesNotExist:
            return Response({'detail': 'Invalid code'}, status=400)

        if code_obj.is_expired():
            return Response({'detail': 'Code expired'}, status=400)

        if code_obj.code != code:
            return Response({'detail': 'Incorrect code'}, status=400)

        user = code_obj.profile.user
        login(request, user) 

        profile = code_obj.profile
        if not profile.invite_code:
            profile.generate_invite_code()
            profile.save()

        return Response({
            'detail': 'Logged in',
            'username': user.username,
            'invite_code': profile.invite_code
        })



class ActivatedInviteCodedAPI(APIView):
    """
    Активация инвайт-кода от другого пользователя.

    Доступ: только авторизованные пользователи.

    Параметры:
    - activated_invite (str): инвайт-код приглашённого пользователя.
    
    Ответ:
    - message (str): результат активации.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        activated_code = request.data.get('activated_invite')
        if not activated_code:
            return Response({'error': 'Invite code is required'}, status=400)

        try:
            inviter_profile = Profile.objects.get(invite_code=activated_code)
        except Profile.DoesNotExist:
            return Response({'error': 'Invalid invite code'}, status=404)

        current_profile = request.user.profile

        if current_profile.activated_invite is not None:
            return Response({'error': 'Invite code has already been activated'}, status=400)

        if inviter_profile == current_profile:
            return Response({'error': 'You cannot activate your own code'}, status=400)

        if inviter_profile.activated_invite == current_profile:
            return Response({'error': 'Mutual invite activation is not allowed'}, status=400)

        current_profile.activated_invite = inviter_profile
        current_profile.save()

        return Response({'message': f'Invite code {activated_code} activated successfully'})
    
    
class ProfileAPI(APIView):
    """
    Получение информации о текущем пользователе и его приглашённых.

    Доступ: только авторизованные пользователи.

    Ответ:
    - user (object): данные пользователя.
    - referrals (list): список профилей, активировавших его инвайт-код.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user
        current_profile = current_user.profile
        user_data = UserWithProfileSerializer(current_user).data
        invited_profiles = Profile.objects.filter(activated_invite=current_profile)
        referrals_data = ProfileSerializer(invited_profiles, many=True).data
        
        return Response({
            'user': user_data,
            'referrals': referrals_data
        })