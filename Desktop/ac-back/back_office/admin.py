from django.contrib import admin

# Register your models here.
from back_office.models import PriceForPosition
from directory.models import TypeOfAccrualRules


class TypeOfAccrualRulesInline(admin.TabularInline):
    model = TypeOfAccrualRules


class PriceForPositionAdmin(admin.ModelAdmin):
    inlines = [TypeOfAccrualRulesInline, ]


admin.site.register(PriceForPosition)