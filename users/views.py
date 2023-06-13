from django.core.exceptions import ObjectDoesNotExist
from django.utils.datetime_safe import datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_phone
from .serializers import SignUpSerializers, ChangeUserInformation, PhotoUpdateSerializer, LoginSerializer, \
    LoginRefreshTokenSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .models import UserModel, ONE, CODE_STEP, EMAIL, PHONE
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import permissions


# SIGNUP UCHUN YOZILGAN VIEW


class CreateUserView(CreateAPIView):
    queryset = UserModel.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializers


# SMS YOKI EMAILGA KELGAN PAROLNI TASDIQLASH UCHUN YOZILGAN VIEW


class VerifyCodeApiView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                'success': True,
                'auth_step': user.auth_step,
                'access': user.token()['access_token'],
                'refresh': user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(end_time__gte=datetime.now(), code=code, is_confirm=False)
        if not verifies.exists():
            data = {
                'massage': "Tasdiqlash kodingiz yaroqsiz"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirm=True)
        if user.auth_step == ONE:
            user.auth_step = CODE_STEP
            user.save()
        return True



# AGAR TASDIQLASH CODINI JO'NATA OLINMASA QAYTADAN JO'NATISH UCHUN YPZILGAN VIEW


class GetCodeApiView(APIView):
    def get(self, *args, **kwargs):
        user = self.request.user
        self.check_verify_again(user)
        if user.auth_type == EMAIL:
            code = user.create_code(EMAIL)
            send_email(user.email, code)
        elif user.auth_type == PHONE:
            code = user.create_code(PHONE)
            send_email(user.phone_number, code)
            print(code)
        else:
            data = {
                'message': "Email yoki telefon raqamingiz noto'g'ri"
            }
            raise ValidationError(data)


        return Response(
            {
                "success": True,
                "message": "Tasdiqlash codingiz qaytadan jo'natildi"
            }
        )



    @staticmethod
    def check_verify_again(user):
        verifies = user.verify_codes.filter(end_time__gte=datetime.now(), is_confirm=False)
        if verifies.exists():
            data = {
                'massage': "Kodingiz ishlatish uchun yaroqli biroz kuting !"
            }
            raise ValidationError(data)



# USERNAME, PASSWORD VA FORMALARNI TO'LDIRISH VA YANGILASH UCHUN YOZILGAN VIEW


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user
    

    # THIS METHOD IS FOR {PUT}
    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)

        data = {
            'success': True,
            "message": "User muvaffaqiyatli tarzda yangilandi",
            "auth_step": request.user.auth_step
        }

        return Response(data, status=200)


    # THIS METHOD IS FOR {PATCH}
    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)

        data = {
            'success': True,
            "message": "User muvaffaqiyatli tarzda yangilandi",
            "auth_step": request.user.auth_step
        }

        return Response(data, status=200)



# RASMNI QO'YISH UCHUN YOZILGAN VIEW


class PhotoUpdateView(APIView):
    permission_classes = [IsAuthenticated, ]


    def put(self, request, *args, **kwargs):
        serializers = PhotoUpdateSerializer(data=request.data)
        if serializers.is_valid():
            user = request.user
            serializers.update(user, serializers.validated_data)
            return Response({
                'message': "Rasm muvaffaqiyatli tarzda o'zgartirildi !"
            })
        else:
            return Response(
                serializers.errors, status=400
            )


# LOGIN UCHUN VIEW

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer



# REFRESH TOKEN ORQALI ACCESS TOKENNI YANGILASH UCHUN YOZILGAN VIEW


class RefreshTokenView(TokenRefreshView):
    serializer_class = LoginRefreshTokenSerializer



# LOGOUT UCHUN YOZILGAN VIEW



class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': "Siz muvaffaqiyatli tarzda accountingizdan chiqdingiz"
            }
            Response(data, status=205)
        except TokenError:
            Response(status=400)



# FORGOT PASSWORD UCHUN YOZIGAN VIEW


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get("user")
        if check_email_phone(email_or_phone) == 'email':
            code = user.create_code(EMAIL)
            send_email(email_or_phone, code)
        elif check_email_phone(email_or_phone) == 'phone_number':
            code = user.create_code(PHONE)
            send_email(email_or_phone, code)
        return Response(
            {
                'success': True,
                'message': 'Tasdiqlash kodingiz muvaffaqiyatli yuborildi',
                'access': user.token()['access'],
                "refresh": user.token()['refresh'],
                "auth_dtep": user.auth_step
            }, status=200
        )



# RESET PASSWORD UCHUN YOZILGAN VIEW

class ResetPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ResetPasswordSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = UserModel.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist:
            raise NotFound(detail='Foydalanuvchi topilmadi')

        return Response(
            {
                'success':True,
                "message": 'Parolingiz muvaffaqiyatli o\'zgartirildi !',
                'access': user.token()['access_token'],
                'refresh': user.token()['refresh_token']
            }
        )



























