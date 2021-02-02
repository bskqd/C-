from django.contrib import admin

from directory.models import Speciality, NZ, Specialization


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name_ukr', 'is_disable')
    search_fields = ('name_ukr',)


@admin.register(NZ)
class NZAdmin(admin.ModelAdmin):
    list_display = ('name_ukr', 'is_disable')
    search_fields = ('name_ukr',)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_ukr', 'is_disable')
    search_fields = ('name_ukr',)
