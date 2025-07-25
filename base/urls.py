from django.urls import path, include
from .views import ProfileAPI, SendCodeView, UserWithProfileViewSet, VerifyCodeView, ActivatedInviteCodedAPI

urlpatterns = [
    path('register/', UserWithProfileViewSet.as_view(), name='register'),
    path('send-code/', SendCodeView.as_view(), name='send-code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('profile/', ProfileAPI.as_view(), name='profile'),
    path('profile/activate-code/', ActivatedInviteCodedAPI.as_view(), name='activate_code'),
]