from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'preferred_temperature_unit')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('preferred_temperature_unit',)
