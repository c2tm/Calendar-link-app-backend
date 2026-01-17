from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, IcsFile, Subscription

# Register your models here.

UserAdmin.fieldsets += ('Custom fields set', {'fields': ('tokens','bypass_token_limit')}),
admin.site.register(User, UserAdmin)
admin.site.register(IcsFile)
admin.site.register(Subscription)
