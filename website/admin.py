from django.contrib import admin
from django.utils.html import format_html
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'vacancy', 'created_at')
    search_fields = ('name', 'email', 'phone', 'vacancy__title')
    list_filter = ('vacancy', 'created_at')
    readonly_fields = ('created_at', 'custom_fields_display')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ('vacancy', 'name', 'email', 'phone', 'location', 'cover_letter')
            }),
            ('Custom Fields', {
                'fields': ('custom_fields_display',),
            }),
            ('Timestamps', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            })
        ]
        return fieldsets
    
    def custom_fields_display(self, obj):
        if not obj.answers:
            return "No custom fields"
        
        html = '<table class="table">'
        html += '<tr><th>Field</th><th>Answer</th></tr>'
        
        for field_id, answer in obj.answers.items():
            field = obj.vacancy.fields.filter(id=field_id).first()
            if field:
                field_name = field.label_uz  # or label_ru based on your preference
                html += f'<tr><td>{field_name}</td><td>{answer}</td></tr>'
        
        html += '</table>'
        return format_html(html)
    
    custom_fields_display.short_description = 'Custom Fields'
