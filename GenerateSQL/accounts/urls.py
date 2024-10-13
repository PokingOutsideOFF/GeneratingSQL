from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    # path('verify-otp/',VerifyOTPView.as_view(), name="verify-otp"),
    # path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('users/', GetUserView.as_view(), name='users'),
    path('create-user/', CreateUser.as_view(), name="create-user"),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('generate-sql/', GenerateSqlQuery.as_view(), name="generate-sql")
]
