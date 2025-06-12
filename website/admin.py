from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'vacancy', 'email', 'phone', 'created_at')
    list_filter = ('vacancy', 'created_at')
    search_fields = ('name', 'email', 'phone', 'vacancy__title')
    readonly_fields = ('created_at',)
