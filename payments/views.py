# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

import logging
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)
from azbankgateways.exceptions import AZBankGatewaysException

from .models import Payment
from cars.models import Car, Motorcycle, HeavyVehicle

logger = logging.getLogger(__name__)


@login_required
def start_payment(request, vehicle_type, vehicle_id):
    """شروع فرآیند پرداخت (نسخه 2.3.4)"""
    
    # ✅ دریافت وسیله نقلیه
    if vehicle_type == 'car':
        vehicle = get_object_or_404(Car, id=vehicle_id)
    elif vehicle_type == 'motorcycle':
        vehicle = get_object_or_404(Motorcycle, id=vehicle_id)
    elif vehicle_type == 'heavy':
        vehicle = get_object_or_404(HeavyVehicle, id=vehicle_id)
    else:
        messages.error(request, 'نوع وسیله نقلیه نامعتبر است.')
        return redirect('cars:car_list')
    
    # ✅ بررسی دسترسی
    if vehicle.seller != request.user:
        messages.error(request, 'شما به این آگهی دسترسی ندارید.')
        return redirect('cars:car_list')
    
    if vehicle.is_paid:
        messages.info(request, 'این آگهی قبلاً پرداخت شده است.')
        return redirect('cars:car_list')
    
    if vehicle.is_draft:
        messages.error(request, 'این آگهی هنوز تکمیل نشده است.')
        return redirect('cars:car_list')
    
    amount = vehicle.payment_amount
    if amount <= 0:
        messages.error(request, 'مبلغ پرداخت نامعتبر است.')
        return redirect('cars:car_list')
    
    # ✅ ساخت Payment
    payment = Payment.objects.create(
        user=request.user,
        vehicle_type=vehicle_type,
        vehicle_id=vehicle_id,
        amount=amount,
        status='pending',
        description=f'پرداخت برای آگهی: {vehicle.title}',
    )
    
    amount_rial = int(amount) * 10
    
    try:
        # ✅ ساخت BankFactory
        factory = bankfactories.BankFactory()
        bank = factory.create(bank_type=bank_models.BankType.ZARINPAL)
        
        # ✅ تنظیم درخواست
        bank.set_request(request)
        bank.set_amount(amount_rial)
        
        # ✅ Callback URL
        callback_url = request.build_absolute_uri(reverse('payments:callback'))
        bank.set_client_callback_url(callback_url)
        
        # ✅ ذخیره رکورد
        bank_record = bank.ready()
        
        # ✅ ذخیره کد پیگیری
        payment.tracking_code = bank_record.tracking_code
        payment.gateway_name = 'zarinpal'
        payment.save()
        
        # ✅ هدایت به درگاه
        return bank.redirect_gateway()
    
    except AZBankGatewaysException as e:
        logger.error(f"خطا در ساخت درگاه: {e}")
        payment.mark_as_failed(description=str(e))
        messages.error(request, 'خطا در اتصال به درگاه پرداخت. لطفاً دوباره تلاش کنید.')
        return redirect('cars:car_list')


@login_required
def payment_callback(request):
    """بازگشت از درگاه پرداخت (نسخه 2.3.4)"""
    
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    
    if not tracking_code:
        messages.error(request, 'کد پیگیری یافت نشد.')
        return redirect('cars:car_list')
    
    try:
        # ✅ دریافت تراکنش از دیتابیس پکیج
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        messages.error(request, 'تراکنش یافت نشد.')
        return redirect('cars:car_list')
    
    # ✅ دریافت Payment
    payment = Payment.objects.filter(tracking_code=tracking_code).first()
    if not payment:
        messages.error(request, 'تراکنش در سیستم یافت نشد.')
        return redirect('cars:car_list')
    
    # ✅ بررسی وضعیت
    if bank_record.is_success:
        # ✅ پرداخت موفق
        payment.mark_as_success(reference_id=bank_record.tracking_code)
        # ✅ فعال کردن آگهی
        vehicle = None
        if payment.vehicle_type == 'car':
            vehicle = Car.objects.filter(id=payment.vehicle_id).first()
        elif payment.vehicle_type == 'motorcycle':
            vehicle = Motorcycle.objects.filter(id=payment.vehicle_id).first()
        elif payment.vehicle_type == 'heavy':
            vehicle = HeavyVehicle.objects.filter(id=payment.vehicle_id).first()
        
        if vehicle:
            vehicle.is_paid = True
            vehicle.is_active = True
            vehicle.is_verified = False
            vehicle.payment_date = timezone.now()
            vehicle.payment_tracking_code = tracking_code
            vehicle.save()
            
            messages.success(request, '🎉 پرداخت با موفقیت انجام شد!')
            
            if payment.vehicle_type == 'car':
                return redirect('cars:car_detail', pk=vehicle.pk, slug=vehicle.slug)
            elif payment.vehicle_type == 'motorcycle':
                return redirect('cars:motorcycle_detail', pk=vehicle.pk, slug=vehicle.slug)
            elif payment.vehicle_type == 'heavy':
                return redirect('cars:heavy_detail', pk=vehicle.pk, slug=vehicle.slug)
        
        messages.success(request, '🎉 پرداخت با موفقیت انجام شد!')
        return redirect('cars:car_list')
    
    else:
        # ❌ پرداخت ناموفق
        payment.mark_as_failed(description='پرداخت ناموفق بود')
        messages.error(request, '❌ پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.')
        return redirect('cars:car_list')


@login_required
def payment_history(request):
    """تاریخچه پرداخت‌های کاربر"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/payment_history.html', context)