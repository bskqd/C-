from django.contrib import admin

from news.models import News
# Register your models here.


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('author',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()
