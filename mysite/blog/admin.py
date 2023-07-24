from django.contrib import admin
from django import forms
from .models import Cities_maps

@admin.register(Cities_maps)
class Cities_mapsAdmin(admin.ModelAdmin):
    list_display = ('city_name_client', 'city_name_product')
    list_filter = ('city_name_client', 'city_name_product')
    search_fields = ('city_name_client', 'city_name_product')
    ordering = ('city_name_client', 'city_name_product')