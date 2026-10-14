# payments/admin.py
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'vehicle_type', 'amount', 
        'status', 'tracking_code', 'created_at'
    )
    list_filter = ('status', 'vehicle_type', 'created_at')
    search_fields = (
        'user__username', 'tracking_code', 
        'reference_id', 'vehicle_id'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'paid_at'
    )
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات آگهی', {
            'fields': ('vehicle_type', 'vehicle_id')
        }),
        ('اطلاعات پرداخت', {
            'fields': ('amount', 'status', 'gateway_name', 'tracking_code', 'reference_id')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
    )
    
    actions = ['mark_as_success', 'mark_as_failed']
    
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} تراکنش به عنوان موفق علامت‌گذاری شد.')
    mark_as_success.short_description = '✅ علامت‌گذاری به عنوان موفق'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} تراکنش به عنوان ناموفق علامت‌گذاری شد.')
    mark_as_failed.short_description = '❌ علامت‌گذاری به عنوان ناموفق'