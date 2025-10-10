from django.contrib import admin
from .models import Complaint, AdminProfile, ComplaintTracking, StaffMember
from django.utils.html import format_html

class ComplaintTrackingInline(admin.TabularInline):
    model = ComplaintTracking
    extra = 0
    readonly_fields = ['updated_at', 'updated_by']
    fields = ['status', 'notes', 'updated_by', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'complaint_id', 
        'name', 
        'location', 
        'status_badge', 
        'created_at', 
        'photo_admin_preview', 
        'qr_code_admin_preview'
    ]
    
    list_filter = [
        'status', 
        'created_at', 
        'location',
        'verified_at',
        'resolved_at'
    ]
    
    search_fields = [
        'complaint_id', 
        'name', 
        'location', 
        'issue',
        'description'
    ]
    
    readonly_fields = [
        'complaint_id', 
        'created_at', 
        'verified_at', 
        'resolved_at', 
        'timestamp',
        'photo_admin_preview',
        'qr_code_admin_preview',
        'status_timeline'
    ]
    
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    inlines = [ComplaintTrackingInline]
    
    fieldsets = (
        ('📝 बेसिक जानकारी', {
            'fields': (
                'complaint_id',
                'name', 
                'location', 
                'issue', 
                'description',
                'photo',
                'photo_admin_preview'
            )
        }),
        
        ('🖼️ मीडिया फाइल्स', {
            'fields': (
                'voice_note',
                'qr_code',
                'qr_code_admin_preview'
            )
        }),
        
        ('📊 स्टेटस ट्रैकिंग', {
            'fields': (
                'status',
                'feedback',
                'status_timeline',
                'assigned_staff', 
                'escalated_to'
            )
        }),
        
        ('⏰ टाइमस्टैम्प्स', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'verified_at',
                'resolved_at',
                'timestamp'
            )
        }),
        
        ('🏆 परफॉर्मेंस मेट्रिक्स', {
            'classes': ('collapse',),
            'fields': (
                'sla_breached', 
                'trust_badge'
            )
        }),
    )
    
    # Custom methods for admin display
    def status_badge(self, obj):
        status_colors = {
            'submitted': 'orange',
            'verified': 'blue', 
            'resolved': 'green',
            'feedback': 'purple',
            'performance': 'teal',
            'escalation': 'red',
            'dashboard': 'gray'
        }
        
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'स्थिति'
    status_badge.admin_order_field = 'status'
    
    def photo_admin_preview(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank" style="display: block; text-align: center;">'
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 8px; border: 2px solid #ddd;" />'
                '<br/><small>📸 फोटो देखें</small>'
                '</a>',
                obj.photo.url,
                obj.photo.url
            )
        return "❌ कोई फोटो नहीं"
    photo_admin_preview.short_description = 'फोटो प्रिव्यू'
    
    def qr_code_admin_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<a href="{}" target="_blank" style="display: block; text-align: center;">'
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 8px; border: 2px solid #007bff;" />'
                '<br/><small>📱 QR कोड देखें</small>'
                '</a>',
                obj.qr_code.url,
                obj.qr_code.url
            )
        return "❌ QR कोड जनरेट नहीं हुआ"
    qr_code_admin_preview.short_description = 'QR कोड'
    
    def status_timeline(self, obj):
        timeline = []
        if obj.created_at:
            timeline.append(f"✅ दर्ज हुई: {obj.created_at.strftime('%d/%m/%Y %H:%M')}")
        if obj.verified_at:
            timeline.append(f"🔵 सत्यापित: {obj.verified_at.strftime('%d/%m/%Y %H:%M')}")
        if obj.resolved_at:
            timeline.append(f"🟢 हल हुई: {obj.resolved_at.strftime('%d/%m/%Y %H:%M')}")
        
        if not timeline:
            return "⏳ कोई एक्टिविटी नहीं"
        
        return format_html('<br>'.join(timeline))
    status_timeline.short_description = 'स्टेटस टाइमलाइन'
    
    # Admin actions
    actions = ['mark_as_verified', 'mark_as_resolved']
    
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(status='verified', verified_at=timezone.now())
        self.message_user(request, f'{updated} शिकायतें सत्यापित की गईं')
    mark_as_verified.short_description = 'चयनित शिकायतें सत्यापित करें'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} शिकायतें हल की गईं')
    mark_as_resolved.short_description = 'चयनित शिकायतें हल करें'
    
    # Save method to track changes
    def save_model(self, request, obj, form, change):
        if change:
            # Create tracking record if status changed
            if 'status' in form.changed_data:
                ComplaintTracking.objects.create(
                    complaint=obj,
                    status=obj.status,
                    notes=f'Admin द्वारा स्थिति अपडेट की गई',
                    updated_by=request.user
                )
        super().save_model(request, obj, form, change)

class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'village_name', 'phone_number', 'is_active', 'created_at']
    list_filter = ['village_name', 'is_active', 'created_at']
    search_fields = ['user__username', 'village_name', 'phone_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('👤 यूज़र जानकारी', {
            'fields': ('user', 'village_name')
        }),
        ('📞 संपर्क', {
            'fields': ('phone_number',)
        }),
        ('⚙️ सेटिंग्स', {
            'fields': ('is_active', 'created_at')
        }),
    )

class ComplaintTrackingAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'status_badge', 'updated_by', 'updated_at']
    list_filter = ['status', 'updated_at', 'updated_by']
    search_fields = ['complaint__complaint_id', 'complaint__name', 'notes']
    readonly_fields = ['updated_at']
    date_hierarchy = 'updated_at'
    
    def status_badge(self, obj):
        status_colors = {
            'submitted': 'orange',
            'verified': 'blue', 
            'resolved': 'green',
            'feedback': 'purple',
            'performance': 'teal',
            'escalation': 'red',
            'dashboard': 'gray'
        }
        
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">{}</span>',
            color,
            obj.complaint.get_status_display_hindi()
        )
    status_badge.short_description = 'स्थिति'

class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'admin_profile', 'designation', 'phone_number', 'is_active']
    list_filter = ['designation', 'is_active', 'admin_profile__village_name']
    search_fields = ['user__username', 'designation', 'phone_number']
    readonly_fields = ['user_info']
    
    fieldsets = (
        ('👥 स्टाफ जानकारी', {
            'fields': ('user', 'admin_profile', 'designation')
        }),
        ('📞 संपर्क', {
            'fields': ('phone_number',)
        }),
        ('⚙️ सेटिंग्स', {
            'fields': ('is_active',)
        }),
    )
    
    def user_info(self, obj):
        return f"Username: {obj.user.username} | Email: {obj.user.email}"
    user_info.short_description = 'यूज़र जानकारी'

# Register all models
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)
admin.site.register(ComplaintTracking, ComplaintTrackingAdmin)
admin.site.register(StaffMember, StaffMemberAdmin)

# Admin site customization
admin.site.site_header = '🌐 AwazGram - एडमिन पैनल'
admin.site.site_title = 'AwazGram Admin'
admin.site.index_title = 'वेलकम टू AwazGram एडमिन पैनल'