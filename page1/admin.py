from django.contrib import admin
from .models import Complaint
from django.utils.html import format_html

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'qr_code', 
        'villager_name', 
        'get_category_display', 
        'status', 
        'location', 
        'created_at'
    ]
    
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['villager_name', 'location', 'qr_code']
    readonly_fields = ['created_at', 'qr_code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('villager_name', 'location', 'category', 'description', 'qr_code')
        }),
        ('Media', {
            'fields': ('photo', 'voice_note')
        }),
        ('Status', {
            'fields': ('status', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'verified_at', 'resolved_at', 'escalated_at')
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('qr_code',)
        return self.readonly_fields