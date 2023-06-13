import re
import threading

from decouple import config
from django.core import validators
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
import phonenumbers
from twilio.rest import Client


email_regax = re.compile(r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+')
phone_reagx = re.compile(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$')

def check_email_phone(phone_or_email):
    # phone = phonenumbers.parse(phone_or_email)
    if re.fullmatch(email_regax, phone_or_email):
        phone_or_email = 'email'
    elif re.fullmatch(phone_reagx, phone_or_email):
        phone_or_email = 'phone_number'
    else:
        data = {
            'status': False,
            'message': 'Telefon raqamingiz yoki emailingiz noto\'g\'ri kiritildi'
        }
        raise ValueError(data)

    return phone_or_email




class EamilThred(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == "html":
            email.content_subtype = "html"
        EamilThred(email).start()

def send_email(email, code):
    html_content = render_to_string(
        'email/auth/activate.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            'body': html_content,
            "to_email": email,
            "content_type": "html"
        }
    )


def send_code_phone(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Salom sizning tasdiqlash kodingiz {code}",
        from_="+9981234567",
        to=f"{phone}"
    )



# LOGIN UCHUN USERNAME, PHONE, EMAIL UCHUN TEKSHIRISH FUNKSIYASI



username_regax = re.compile(r"^[A-z0-9_-]{3,15}$")

def check_user_type(user_input):
    if re.fullmatch(email_regax, user_input):
        user_input = 'email'

    elif re.fullmatch(phone_reagx, user_input):
        user_input = 'phone_number'

    elif re.fullmatch(username_regax, user_input):
        user_input = 'username'

    else:
        data = {
            'status': False,
            'massage': 'telefon raqamingiz, foydalanuvchi nomingiz yoki emailingiz xato kiritildi'
        }
        raise ValidationError(data)

    return user_input





















































