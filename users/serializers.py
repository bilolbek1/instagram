from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db.models import Q
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_phone, check_user_type
from .models import UserModel, PHONE, EMAIL, ONE, CODE_STEP, DONE, PHOTO_STEP
from shared.utility import send_email


# SIGNUP UCHUN YOZILGAN SERIALIZER


class SignUpSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_step = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializers, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)


    class Meta:
        model = UserModel
        fields = (
            'id',
            'auth_type',
            'auth_step'
        )

    def create(self, validated_data):
        user = super(SignUpSerializers, self).create(validated_data)
        print(user)
        if user.auth_type == EMAIL:
            code = user.create_code(EMAIL)
            send_email(user.email, code)
        elif user.auth_type == PHONE:
            code = user.create_code(PHONE)
            print(code)
            send_email(user.phone_number, code)
            # send_code_phone = (user.phone_number, code)
        user.save()
        return user




    def validate(self, data):
        super(SignUpSerializers, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_phone(user_input)
        print('user_input', user_input)
        print('input_type', input_type)
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': EMAIL
            }
        elif input_type == 'phone_number':
            data = {
                'phone_number': user_input,
                'auth_type': PHONE
            }

        else:
            data = {
                'success': False,
                'massage': 'Siz email yoki telefon raqamingizni kiritishingiz kerak'
            }
            raise ValidationError(data)
        return data


    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and UserModel.objects.filter(email=value).exists():
            data = {
                'success': False,
                'massage': "Bu email allaqachon ro'yxatdan o'tgan !"
            }
            raise ValidationError(data)

        elif value and UserModel.objects.filter(phone_number=value).exists():
            data = {
                'sucess': False,
                "massage": "Bu raqam bilan allaqachon ro'yxatdan o'tib bo'lingan !"
            }

            raise ValidationError(data)

        return value



    def to_representation(self, instance):
        print('to_rep', instance)
        data = super(SignUpSerializers, self).to_representation(instance)
        data.update(instance.token())


        return data





# USERNAME PASSWORD FORMALARNI TO'LDIRISH VA YANGILASH UCHUN YOZILGAN SERIALIZERS'



class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


    def validate(self, data):
        passowrd = data.get('password', None)
        confirm_password = data.get('password', None)
        if passowrd != confirm_password:
            data = {
                'massage': "Parolingiz va tasdiqlash parolingiz bir xil emas !"
            }
            raise ValidationError(data)
        if passowrd:
            validate_password(passowrd)
            validate_password(confirm_password)

        return data


    def validate_username(self, username):
        if len(username) < 5 or len(username) > 20:
            raise ValidationError(
                {
                    'massage': "Username uzunligi 5 dan 20 ta belgi uzunligicha "
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    'massage': "Username raqamlardan iborat bo'lmasligi kerak !"
                }
            )

        return username


    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_step == CODE_STEP:
            instance.auth_step = DONE
        instance.save()
        return instance




# RASM UCHUN YOZILGAN SERIALIZER


class PhotoUpdateSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg', 'heic', 'heif'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_step = PHOTO_STEP
            instance.save()
        return instance



# LOGINDA EMAIL, PHONE_NUMBER VA USERNAME UCHUN SERIALIZER


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('user_input')
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone_number':
            user = self.get_user(phone_number__iexact=user_input)
            username = user.username

        else:
            data = {
                "success": True,
                "message": "Siz email, username yoki telefon raqamingizni kiritishingiz kerak !"
            }
            raise ValidationError(data)

        authentication_kwargs = {
            self.username_field: username,
            'password': data['password']
        }

        current_user = UserModel.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_step in [ONE, CODE_STEP]:
            raise ValidationError(
                {
                    "success": True,
                    'message': "Siz ro'yxatdan to'liq o'tmagansiz !"
                }
            )
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    "success": True,
                    "message": "Kchirasiz login yoki parolingiz to'liq ema qaytaddan urinib ko'ring !"
                }
            )

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_step in [ONE, CODE_STEP]:
            raise PermissionDenied("Sizda login qilish uchun ruxsat yo'q !")
        data = self.user.token()
        self.fields["auth_step"] = self.user.auth_step
        self.fields["full_name"] = self.user.fullname
        return data



    def get_user(self, **kwargs):
        user = UserModel.objects.filter(**kwargs)
        if not user.exists():
            raise ValidationError({
                "message": "Bunday account topilmadi"
            })
        return user.first()




# from rest_framework import serializers
# from django.contrib.auth import authenticate
# from django.core.exceptions import ValidationError
# from .models import UserModel
#
#
# class LoginSerializer(serializers.Serializer):
#
#     def __init__(self, *args, **kwargs):
#         super(LoginSerializer, self).__init__(*args, **kwargs)
#         self.fields['user_input'] = serializers.CharField(required=True)
#         self.fields['password'] = serializers.CharField(required=False, write_only=True)
#         self.fields['value'] = serializers.CharField(required=False, read_only=True)
#
#     def auth_validate(self, data):
#         user_input = data.get('user_input')
#         password = data.get('password')
#
#
#         user = UserModel.objects.filter(username__iexact=user_input).first()
#         if check_user_type(user_input) == 'username':
#             value = 'username'
#         elif check_user_type(user_input) == 'email':
#             value = 'email'
#         elif check_user_type(user_input) == "phone_number":
#             value = "phone_number"
#         else:
#             raise ValidationError(
#                 {
#                     "success": False,
#                     "message": "Siz email, telefon raqamingiz yoki usernamengizni kiritishingiz kerak."
#                 }
#             )
#
#
#         user = authenticate(username=user.username, password=password)
#         if user.auth_step not in [DONE, PHOTO_STEP]:
#             raise ValidationError("Sizda login qilish uchun ruxsat yo'q!")
#
#         if not user:
#             raise ValidationError("Kirish ma'lumotlari noto'g'ri!")
#
#         self.user = user
#         return value
#
#     def validate(self, data):
#         self.auth_validate(data)
#         return data
#
#     def to_representation(self, instance):
#         token = self.user.token()
#         return {
#             'token': token,
#             'auth_step': self.user.auth_step,
#             'full_name': self.user.fullname
#         }





# REFRESH TOKEN ORQALI ACCESS TOKENNI YANGILASH UCHUN YOZILGAN SEIALIZER



class LoginRefreshTokenSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken('access')
        user_id = access_token_instance['user_id']
        user = get_object_or_404(UserModel, id=user_id)
        update_last_login(None, user)
        return data



# LOGOUT UCHUN SERIALIZER



class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()



# FORGOT PASSWORD UCHUN YOZILGAN SERIALIZER


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    'success': False,
                    "message": "Siz telefon raqamingiz yoki emailingizni kiritishingiz kerak!"
                }
            )
        user = UserModel.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail='Ushbu foydalanuvchi topilmadi')
        attrs['user'] = user.filter()
        return attrs



# RESET PASSWORD UCHUN YOZIGAN SERIALIZER


class ResetPasswordSerializer(serializers.ModelSerializer):
    id =serializers.UUIDField(read_only=True)
    password = serializers.CharField(max_length=8, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=8, write_only=True, required=True)

    class Meta:
        model = UserModel
        fields = ('id', 'password', 'confirm_password')


    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "success": False,
                    'message': 'Password va confirm_password bir xil emas !'
                }
            )
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)











































