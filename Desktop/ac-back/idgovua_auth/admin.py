from django.contrib import admin

# Register your models here.
from idgovua_auth.models import AuthorizationLog


class AuthorizationLogAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'middle_name', 'inn', 'phone', 'datetime')
    ordering = ('datetime', 'inn')
    list_filter = ('datetime',)
    list_display = ('__str__', 'datetime', 'inn', 'phone')


admin.site.register(AuthorizationLog, AuthorizationLogAdmin)
