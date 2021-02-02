from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from user_profile.models import UserProfile, MainGroups, BranchOfficeRestrictionForPermission

User = get_user_model()


class UserProfileToAdmin(admin.StackedInline):
    model = UserProfile
    exclude = ('city',)


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Token'), {'fields': ('JWT', 'token')}),
    )
    readonly_fields = ('JWT', 'token')
    inlines = (UserProfileToAdmin,)

    def JWT(self, instance):
        refresh = RefreshToken.for_user(instance)
        access = refresh.access_token
        access.set_exp(lifetime=timedelta(hours=2))
        return access

    def token(self, instance):
        try:
            token = Token.objects.get(user_id=instance.pk)
            return token.key
        except Token.DoesNotExist:
            return None


admin.site.register(User, CustomUserAdmin)

admin.site.register(UserProfile)

admin.site.register(MainGroups)

admin.site.register(BranchOfficeRestrictionForPermission)
