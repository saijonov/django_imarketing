from django.contrib import admin
from django.utils.html import format_html
from .models import User, Vacancy, Feedback, AboutSection, VacancyField

class VacancyFieldInline(admin.TabularInline):
    model = VacancyField
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastname', 'phone', 'language', 'created_at')
    list_filter = ('language', 'created_at', 'gender')
    search_fields = ('name', 'lastname', 'phone', 'location')
    readonly_fields = ('tg_id', 'created_at')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'short_text_uz', 'short_text_ru')
    inlines = [VacancyFieldInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'is_published')
        }),
        ('Content', {
            'fields': (
                'short_text_uz', 'short_text_ru',
                'full_text_uz', 'full_text_ru',
                'image'
            )
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',),
            'classes': ('collapse',)
        })
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('message', 'user__name', 'user__lastname')
    readonly_fields = ('created_at',)

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at')
