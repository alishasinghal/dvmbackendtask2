from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import OrganizationProfile, Wallet

User = get_user_model()


class OrganizationProfileInline(admin.StackedInline):
    model = OrganizationProfile
    extra = 0
    max_num = 1


class CustomUserAdmin(UserAdmin):
    inlines = [OrganizationProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Wallet)
admin.site.register(OrganizationProfile)