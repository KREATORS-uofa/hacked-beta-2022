from django.contrib import admin
from .models import Data


class DataAdmin(admin.ModelAdmin):
    list_display = ('location', 'reports_2021','reports_2022','sum', 'latitude', 'longitude')

# Register your models here.
admin.site.register(Data, DataAdmin)