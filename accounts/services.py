# accounts/services.py
"""
Services for OTP generation, SMS sending, and other business logic.
"""
import secrets
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from .exceptions import (
    OTPRateLimitError,
    SMSSendingError,
    InvalidPhoneNumberError
)

logger = logging.getLogger(__name__)


class OTPStatus(Enum):
    """Status of OTP operations."""
    SENT = 'sent'
    VERIFIED = 'verified'
    EXPIRED = 'expired'
    BLOCKED = 'blocked'
    INVALID = 'invalid'


@dataclass
class OTPResult:
    """Result of OTP operations."""
    status: OTPStatus
    message: str
    data: Optional[Dict] = None
    remaining_attempts: int = 0
    expires_in: int = 0


class CacheKeys:
    """Cache key patterns for OTP operations."""
    
    @staticmethod
    def otp_code(phone: str) -> str:
        return f'otp_code:{phone}'
    
    @staticmethod
    def otp_attempts(phone: str) -> str:
        return f'otp_attempts:{phone}'
    
    @staticmethod
    def otp_sent_time(phone: str) -> str:
        return f'otp_sent_time:{phone}'
    
    @staticmethod
    def otp_resend_time(phone: str) -> str:
        return f'otp_resend_time:{phone}'
    
    @staticmethod
    def phone_blocked(phone: str) -> str:
        return f'phone_blocked:{phone}'


class BaseSMSService:
    """Base class for SMS services."""
    
    def send_otp(self, phone: str, code: str) -> bool:
        """
        Send OTP code to phone number.
        
        Args:
            phone: Phone number to send to
            code: OTP code to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_service_name(self) -> str:
        """Get name of the SMS service."""
        raise NotImplementedError("Subclasses must implement this method")


class KavenegarService(BaseSMSService):
    """Kavenegar SMS service implementation."""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.sender = self._get_sender_number()
        
    def _get_api_key(self) -> str:
        """Get Kavenegar API key from settings."""
        api_key = getattr(settings, 'KAVENEGAR_API_KEY', None)
        
        if not api_key:
            logger.error("Kavenegar API key not configured in settings")
            raise ImproperlyConfigured(
                "KAVENEGAR_API_KEY must be set in settings for production."
            )
        
        return api_key
    
    def _get_sender_number(self) -> str:
        """Get sender number from settings or use default."""
        return getattr(settings, 'KAVENEGAR_SENDER_NUMBER', '10004346')
    
    def send_otp(self, phone: str, code: str) -> bool:
        """Send OTP via Kavenegar API."""
        try:
            # Import here to avoid dependency issues
            from kavenegar import KavenegarAPI, APIException, HTTPException
            
            api = KavenegarAPI(self.api_key)
            
            params = {
                'sender': self.sender,
                'receptor': phone,
                'message': self._format_message(code),
                'date': None,  # Send immediately
                'type': 'sms',  # Regular SMS
                'localid': self._generate_local_id(phone, code)
            }
            
            # Send SMS
            response = api.sms_send(params)
            
            # Log successful send
            logger.info(
                f"OTP sent via Kavenegar to {phone}. "
                f"Message ID: {response[0]['messageid'] if response else 'N/A'}"
            )
            
            return True
            
        except HTTPException as e:
            logger.error(f"HTTP error in Kavenegar service: {str(e)}")
            raise SMSSendingError(f"خطای شبکه در ارسال پیامک: {str(e)}")
            
        except APIException as e:
            logger.error(f"API error in Kavenegar service: {str(e)}")
            raise SMSSendingError(f"خطای سرویس پیامک: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error in Kavenegar service: {str(e)}")
            raise SMSSendingError(f"خطای ناشناخته در ارسال پیامک")
    
    def _format_message(self, code: str) -> str:
        """Format the SMS message."""
        # Customize message based on your requirements
        message = (
            f"کد تأیید شما: {code}\n"
            f"فروشگاه خودرو - اعتبار: {settings.OTP_EXPIRY_MINUTES} دقیقه"
        )
        return message
    
    @staticmethod
    def _generate_local_id(phone: str, code: str) -> str:
        """Generate a unique local ID for tracking."""
        timestamp = str(int(time.time()))
        hash_input = f"{phone}:{code}:{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:10]
    
    def get_service_name(self) -> str:
        return "Kavenegar"


class DebugSMSService(BaseSMSService):
    """Debug SMS service for development environment."""
    
    def send_otp(self, phone: str, code: str) -> bool:
        """Simulate sending OTP in development."""
        from colorama import Fore, Style, init
        init(autoreset=True)
        
        message = self._format_debug_message(phone, code)
        
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "📱 DEBUG SMS SIMULATION")
        print(Fore.CYAN + "=" * 60)
        print(Fore.YELLOW + message)
        print(Fore.CYAN + "=" * 60)
        
        logger.debug(f"OTP for {phone}: {code}")
        
        return True
    
    def _format_debug_message(self, phone: str, code: str) -> str:
        """Format debug message."""
        current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        expiry_time = (timezone.now() + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )).strftime("%H:%M:%S")
        
        return f"""
        🔐 OTP DEBUG INFORMATION
        ──────────────────────────────────────
        📱 Phone: {phone}
        🔢 OTP Code: {code}
        ⏰ Sent At: {current_time}
        ⏳ Expires At: {expiry_time}
        ⚠️  Valid For: {settings.OTP_EXPIRY_MINUTES} minutes
        ──────────────────────────────────────
        ℹ️  This is a simulation. In production, 
        ℹ️  SMS would be sent via Kavenegar.
        ──────────────────────────────────────
        """
    
    def get_service_name(self) -> str:
        return "Debug"


class SMSFactory:
    """Factory for creating SMS service instances."""
    
    @staticmethod
    def get_service() -> BaseSMSService:
        """
        Get appropriate SMS service based on settings.
        
        Returns:
            BaseSMSService: SMS service instance
        """
        if settings.DEBUG:
            # Use debug service in development
            service_class = DebugSMSService
        else:
            # Use production service
            service_class = getattr(
                settings, 
                'SMS_SERVICE_CLASS', 
                KavenegarService
            )
        
        try:
            return service_class()
        except Exception as e:
            logger.error(f"Failed to initialize SMS service: {str(e)}")
            # Fallback to debug service
            return DebugSMSService()


class OTPService:
    """Main OTP service for managing verification codes."""
    
    def __init__(self):
        self.sms_service = SMSFactory.get_service()
        self.expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
        self.max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 3)
        self.resend_cooldown = getattr(settings, 'OTP_RESEND_COOLDOWN', 60)
        self.block_duration = getattr(settings, 'OTP_BLOCK_DURATION', 3600)
    
    def generate_code(self) -> str:
        """
        Generate a cryptographically secure OTP code.
        
        Returns:
            str: 6-digit OTP code
        """
        # Generate secure random number
        random_num = secrets.randbelow(10 ** 6)
        code = str(random_num).zfill(6)
        
        logger.debug(f"Generated OTP code: {code}")
        return code
    
    def send_otp(self, phone: str) -> OTPResult:
        """
        Send OTP code to phone number with rate limiting.
        
        Args:
            phone: Phone number to send OTP to
            
        Returns:
            OTPResult: Result of the operation
        """
        # Validate phone number
        if not self._validate_phone(phone):
            raise InvalidPhoneNumberError("شماره موبایل معتبر نیست.")
        
        # Check if phone is blocked
        if self._is_phone_blocked(phone):
            block_until = cache.get(CacheKeys.phone_blocked(phone))
            remaining = int((block_until - time.time()))
            return OTPResult(
                status=OTPStatus.BLOCKED,
                message="این شماره موبایل به دلیل تلاش‌های زیاد مسدود شده است.",
                data={'blocked_until': block_until},
                expires_in=remaining
            )
        
        # Check resend cooldown
        if not self._can_resend_otp(phone):
            return OTPResult(
                status=OTPStatus.BLOCKED,
                message=f"لطفاً {self.resend_cooldown} ثانیه دیگر مجدداً تلاش کنید.",
                data={'cooldown': self.resend_cooldown},
                expires_in=self._get_resend_cooldown_remaining(phone)
            )
        
        # Generate OTP code
        code = self.generate_code()
        
        # Store OTP data in cache
        self._store_otp_data(phone, code)
        
        # Send OTP via SMS service
        try:
            success = self.sms_service.send_otp(phone, code)
            
            if success:
                logger.info(f"OTP sent successfully to {phone}")
                return OTPResult(
                    status=OTPStatus.SENT,
                    message="کد تأیید با موفقیت ارسال شد.",
                    data={
                        'phone': phone,
                        'code': code if settings.DEBUG else None,
                        'expires_in': self.expiry_minutes * 60
                    },
                    expires_in=self.expiry_minutes * 60
                )
            else:
                logger.error(f"Failed to send OTP to {phone}")
                return OTPResult(
                    status=OTPStatus.INVALID,
                    message="خطا در ارسال پیامک. لطفاً مجدداً تلاش کنید.",
                    data={'error': 'sms_sending_failed'}
                )
                
        except SMSSendingError as e:
            logger.error(f"SMS sending error for {phone}: {str(e)}")
            return OTPResult(
                status=OTPStatus.INVALID,
                message=str(e),
                data={'error': 'sms_service_error'}
            )
    
    def verify_otp(self, phone: str, entered_code: str) -> OTPResult:
        """
        Verify OTP code.
        
        Args:
            phone: Phone number
            entered_code: Code entered by user
            
        Returns:
            OTPResult: Verification result
        """
        # Check if phone is blocked
        if self._is_phone_blocked(phone):
            return OTPResult(
                status=OTPStatus.BLOCKED,
                message="این شماره موبایل به دلیل تلاش‌های زیاد مسدود شده است.",
                data={'blocked': True}
            )
        
        # Get stored OTP data
        stored_data = self._get_otp_data(phone)
        
        if not stored_data:
            return OTPResult(
                status=OTPStatus.EXPIRED,
                message="کد تأیید منقضی شده یا یافت نشد.",
                data={'expired': True}
            )
        
        stored_code, sent_time = stored_data
        
        # Check if OTP has expired
        if self._is_otp_expired(sent_time):
            self._clear_otp_data(phone)
            return OTPResult(
                status=OTPStatus.EXPIRED,
                message="کد تأیید منقضی شده است.",
                data={'expired': True}
            )
        
        # Increment attempts
        attempts = self._increment_attempts(phone)
        
        # Check max attempts
        if attempts > self.max_attempts:
            self._block_phone(phone)
            return OTPResult(
                status=OTPStatus.BLOCKED,
                message="تعداد تلاش‌های شما بیش از حد مجاز است.",
                data={'blocked': True, 'attempts': attempts},
                remaining_attempts=0
            )
        
        # Verify code
        if entered_code == stored_code:
            # Clear OTP data on successful verification
            self._clear_otp_data(phone)
            self._clear_attempts(phone)
            
            logger.info(f"OTP verified successfully for {phone}")
            return OTPResult(
                status=OTPStatus.VERIFIED,
                message="کد تأیید صحیح است.",
                data={'verified': True, 'phone': phone},
                remaining_attempts=self.max_attempts - attempts
            )
        else:
            remaining = self.max_attempts - attempts
            
            logger.warning(
                f"Invalid OTP attempt for {phone}. "
                f"Attempts: {attempts}/{self.max_attempts}"
            )
            
            return OTPResult(
                status=OTPStatus.INVALID,
                message=f"کد نادرست است. {remaining} تلاش باقی مانده.",
                data={'invalid': True, 'attempts': attempts},
                remaining_attempts=remaining
            )
    
    def resend_otp(self, phone: str) -> OTPResult:
        """
        Resend OTP code with cooldown check.
        
        Args:
            phone: Phone number to resend OTP to
            
        Returns:
            OTPResult: Result of the operation
        """
        return self.send_otp(phone)
    
    def get_otp_status(self, phone: str) -> Dict[str, Any]:
        """
        Get current OTP status for a phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            Dict: OTP status information
        """
        stored_data = self._get_otp_data(phone)
        attempts = self._get_attempts(phone)
        is_blocked = self._is_phone_blocked(phone)
        can_resend = self._can_resend_otp(phone)
        
        status = {
            'has_active_otp': bool(stored_data),
            'attempts': attempts,
            'max_attempts': self.max_attempts,
            'is_blocked': is_blocked,
            'can_resend': can_resend,
            'remaining_attempts': max(0, self.max_attempts - attempts)
        }
        
        if stored_data:
            code, sent_time = stored_data
            expires_at = sent_time + (self.expiry_minutes * 60)
            status.update({
                'expires_in': max(0, expires_at - time.time()),
                'total_expiry': self.expiry_minutes * 60
            })
        
        if not can_resend:
            status['resend_cooldown'] = self._get_resend_cooldown_remaining(phone)
        
        return status
    
    # Private helper methods
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate Iranian phone number format."""
        # Simple validation - can be enhanced
        import re
        pattern = r'^09[0-9]{9}$'
        return bool(re.match(pattern, phone))
    
    def _store_otp_data(self, phone: str, code: str):
        """Store OTP data in cache."""
        sent_time = time.time()
        expiry = self.expiry_minutes * 60
        
        # Store code and sent time
        cache.set(CacheKeys.otp_code(phone), code, expiry)
        cache.set(CacheKeys.otp_sent_time(phone), sent_time, expiry)
        
        # Set resend cooldown
        cache.set(
            CacheKeys.otp_resend_time(phone), 
            sent_time + self.resend_cooldown, 
            self.resend_cooldown
        )
        
        # Reset attempts
        cache.set(CacheKeys.otp_attempts(phone), 0, expiry)
    
    def _get_otp_data(self, phone: str) -> Optional[Tuple[str, float]]:
        """Get stored OTP data from cache."""
        code = cache.get(CacheKeys.otp_code(phone))
        sent_time = cache.get(CacheKeys.otp_sent_time(phone))
        
        if code and sent_time:
            return code, sent_time
        return None
    
    def _clear_otp_data(self, phone: str):
        """Clear OTP data from cache."""
        cache.delete(CacheKeys.otp_code(phone))
        cache.delete(CacheKeys.otp_sent_time(phone))
        cache.delete(CacheKeys.otp_resend_time(phone))
    
    def _increment_attempts(self, phone: str) -> int:
        """Increment OTP verification attempts."""
        key = CacheKeys.otp_attempts(phone)
        attempts = cache.get(key, 0)
        attempts += 1
        
        # Update attempts with extended expiry
        expiry = self.expiry_minutes * 60
        cache.set(key, attempts, expiry)
        
        return attempts
    
    def _get_attempts(self, phone: str) -> int:
        """Get current number of attempts."""
        return cache.get(CacheKeys.otp_attempts(phone), 0)
    
    def _clear_attempts(self, phone: str):
        """Clear attempts counter."""
        cache.delete(CacheKeys.otp_attempts(phone))
    
    def _is_otp_expired(self, sent_time: float) -> bool:
        """Check if OTP has expired."""
        expiry_time = sent_time + (self.expiry_minutes * 60)
        return time.time() > expiry_time
    
    def _can_resend_otp(self, phone: str) -> bool:
        """Check if OTP can be resent."""
        resend_time = cache.get(CacheKeys.otp_resend_time(phone))
        
        if not resend_time:
            return True
        
        return time.time() >= resend_time
    
    def _get_resend_cooldown_remaining(self, phone: str) -> int:
        """Get remaining cooldown time for resending."""
        resend_time = cache.get(CacheKeys.otp_resend_time(phone))
        
        if not resend_time:
            return 0
        
        remaining = int(resend_time - time.time())
        return max(0, remaining)
    
    def _is_phone_blocked(self, phone: str) -> bool:
        """Check if phone number is blocked."""
        blocked_until = cache.get(CacheKeys.phone_blocked(phone))
        
        if not blocked_until:
            return False
        
        if time.time() < blocked_until:
            return True
        
        # Block has expired, clear it
        cache.delete(CacheKeys.phone_blocked(phone))
        return False
    
    def _block_phone(self, phone: str):
        """Block phone number for specified duration."""
        block_until = time.time() + self.block_duration
        cache.set(CacheKeys.phone_blocked(phone), block_until, self.block_duration)
        
        logger.warning(f"Phone number {phone} blocked until {block_until}")


# Singleton instance for easy access
otp_service = OTPService()