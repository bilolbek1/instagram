from django.contrib import admin
from .models import UserModel, UserConfirmation
# Register your models here.

class UserModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'phone_number']

admin.site.register(UserModel, UserModelAdmin)

admin.site.register(UserConfirmation)