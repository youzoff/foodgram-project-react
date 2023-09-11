from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import CustomUser, Subscription

# Delete Group from admin panel
admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_filter = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
