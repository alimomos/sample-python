from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import RegisterUserViewSet,RegisterOtpVerifyViewSet,LogoutAPIView,TokenObtainPairPatchedView,SendOtpAPIView,ResetPasswordAPIView,ChangePasswordAPIView,UserViewSet


urlpatterns = [
    path('register/', RegisterUserViewSet.as_view({'post': 'create'}), name='register'),
    path('register/otp-verify', RegisterOtpVerifyViewSet.as_view({'post': 'create'}), name='register-otp-verify'),
    path('login', TokenObtainPairPatchedView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout', LogoutAPIView.as_view(), name='auth-logout'),
    path('send-otp', SendOtpAPIView.as_view(), name='send-otp'),
    path('reset-password', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('change-password', ChangePasswordAPIView.as_view({'post': 'create'}), name='change-password'),
    path('me',UserViewSet.as_view({'get': 'retrieve','patch':'partial_update'}))
    
]
