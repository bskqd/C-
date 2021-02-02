from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User, HarborMaster, HarborWorker, Agent, UserMarad, HeadAgency, BorderGuard, PortManager


class UserMaradAdmin(admin.StackedInline):
    model = UserMarad
    extra = 0


class HarborMasterAdmin(admin.StackedInline):
    model = HarborMaster
    extra = 0


class HarborWorkerAdmin(admin.StackedInline):
    model = HarborWorker
    extra = 0


class BorderGuardAdmin(admin.StackedInline):
    model = BorderGuard
    extra = 0


class PortManagerAdmin(admin.StackedInline):
    model = PortManager
    extra = 0


class HeadAgencyAdmin(admin.StackedInline):
    model = HeadAgency
    extra = 0


class AgentAdmin(admin.StackedInline):
    model = Agent
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'middle_name', 'email', 'type_user',
                                         'type_authorization')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (UserMaradAdmin, HarborMasterAdmin, HarborWorkerAdmin, AgentAdmin,
               HeadAgencyAdmin, BorderGuardAdmin, PortManagerAdmin)
