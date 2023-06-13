from .views import CreateUserView, VerifyCodeApiView, GetCodeApiView, ChangeUserInformationView, PhotoUpdateView
from .views import LoginView, RefreshTokenView, LogoutView, ForgotPasswordView, ResetPasswordView
from django.urls import path


urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyCodeApiView.as_view()),
    path('new-verify/', GetCodeApiView.as_view()),
    path('update/', ChangeUserInformationView.as_view()),
    path('update/image/', PhotoUpdateView.as_view()),
    path('login/', LoginView.as_view()),
    path('refresh-token/', RefreshTokenView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]


