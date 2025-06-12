from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'vacancy', 'created_at')
    search_fields = ('name', 'email', 'phone', 'vacancy__title')
    list_filter = ('vacancy', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('vacancy', 'name', 'email', 'phone', 'cover_letter', 'extra_question')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
