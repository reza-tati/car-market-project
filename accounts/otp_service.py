# accounts/services/otp_service.py
"""
OTP service for generating and sending verification codes.
"""
import secrets
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class OTPService:
    """Service for OTP operations."""
    
    OTP_LENGTH = 6
    
    @classmethod
    def generate_code(cls) -> str:
        """
        Generate a secure OTP code.
        
        Returns:
            str: 6-digit OTP code
        """
        # Generate cryptographically secure random number
        random_num = secrets.randbelow(10 ** cls.OTP_LENGTH)
        code = str(random_num).zfill(cls.OTP_LENGTH)
        
        logger.debug(f"Generated OTP code: {code}")
        return code
    
    @classmethod
    def send_otp(cls, phone: str, code: str) -> bool:
        """
        Send OTP code to phone number.
        
        Args:
            phone: Phone number
            code: OTP code
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if settings.DEBUG:
                # In development, log the OTP
                cls._log_otp_debug(phone, code)
                return True
            
            # In production, integrate with SMS gateway
            # Example: using Kavenegar, Twilio, etc.
            return cls._send_via_sms_gateway(phone, code)
            
        except Exception as e:
            logger.error(f"Error sending OTP to {phone}: {str(e)}")
            return False
    
    @staticmethod
    def _log_otp_debug(phone: str, code: str):
        """Log OTP in development mode."""
        from django.utils import timezone
        
        logger.info(f"""
        {'='*60}
        📱 OTP DEBUG INFORMATION
        {'='*60}
        Phone: {phone}
        OTP Code: {code}
        Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        Expires in: 5 minutes
        {'='*60}
        """)
    
    @staticmethod
    def _send_via_sms_gateway(phone: str, code: str) -> bool:
        """
        Send OTP via SMS gateway.
        
        Note: Implement your SMS gateway integration here.
        """
        # TODO: Implement actual SMS gateway integration
        # Example with Kavenegar:
        # from kavenegar import KavenegarAPI
        # api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        # params = {
        #     'receptor': phone,
        #     'message': f'کد تأیید شما: {code}'
        # }
        # response = api.sms_send(params)
        
        # For now, return True in development
        return True