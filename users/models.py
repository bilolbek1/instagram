import uuid
from datetime import datetime, timedelta
import random
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel
# Create your models here.

ORDINARY_USER, MANAGER, ADMIN = ('ordinary_user', 'manager', 'admin')
PHONE, EMAIL = ('phone', 'email')
ONE, CODE_STEP, DONE, PHOTO_STEP = ('one', 'code_step', 'done', 'photo_step')


class UserModel(AbstractUser, BaseModel):

    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE = (
        (PHONE, PHONE),
        (EMAIL, EMAIL)
    )
    AUTH_STEP = (
        (ONE, ONE),
        (CODE_STEP, CODE_STEP),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )


    user_type = models.CharField(max_length=33, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=33, choices=AUTH_TYPE)
    auth_step = models.CharField(max_length=33, choices=AUTH_STEP, default=ONE)
    email = models.EmailField(null=True, max_length=254, unique=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, unique=True, blank=True)
    image = models.ImageField(upload_to='user_photos/', blank=True, null=True,
                             validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'heif', 'jpeg', 'heic'])])


    def __str__(self):
        return self.username


    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    def create_code(self, auth_type):
        code = "".join([str(random.randint(1, 10)) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=auth_type,
            code=code
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while UserModel.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(1,9)}"
            self.username = temp_username

    def chek_email(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email


    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password


    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }



    def save(self, *args, **kwargs):
        self.clean()
        super(UserModel, self).save(*args, **kwargs)




    def clean(self):
        self.check_username()
        self.check_pass()
        self.chek_email()
        self.hashing_password()













Phone_Time = 2
Email_Time = 5

class UserConfirmation(BaseModel):

    VERIFY_TYPE = (
        (PHONE, PHONE),
        (EMAIL, EMAIL)
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=33, choices=VERIFY_TYPE)
    user = models.ForeignKey('users.UserModel', models.CASCADE, related_name='verify_codes')
    end_time = models.DateTimeField(null=True)
    is_confirm = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):

        if self.verify_type == PHONE:
            self.end_time = datetime.now() + timedelta(minutes=Phone_Time)
        else:
            self.end_time = datetime.now() + timedelta(minutes=Email_Time)

        super(UserConfirmation, self).save(*args, **kwargs)











































