# accounts/exceptions.py
"""
Custom exceptions for accounts app.
"""

class AccountsBaseError(Exception):
    """Base exception for accounts app."""
    pass


class OTPError(AccountsBaseError):
    """Base exception for OTP related errors."""
    pass


class OTPExpiredError(OTPError):
    """Raised when OTP has expired."""
    def __init__(self, message="کد تأیید منقضی شده است."):
        super().__init__(message)


class OTPAttemptsExceededError(OTPError):
    """Raised when OTP attempts exceed limit."""
    def __init__(self, message="تعداد تلاش‌های شما بیش از حد مجاز است."):
        super().__init__(message)


class OTPRateLimitError(OTPError):
    """Raised when OTP rate limit is exceeded."""
    def __init__(self, message="لطفاً کمی صبر کنید و مجدداً تلاش کنید."):
        super().__init__(message)


class InvalidSessionError(OTPError):
    """Raised when session is invalid or expired."""
    def __init__(self, message="جلسه معتبر نیست. لطفاً مجدداً تلاش کنید."):
        super().__init__(message)


class SMSSendingError(AccountsBaseError):
    """Raised when SMS sending fails."""
    pass


class InvalidPhoneNumberError(AccountsBaseError):
    """Raised when phone number is invalid."""
    def __init__(self, message="شماره موبایل معتبر نیست."):
        super().__init__(message)


class UserProfileError(AccountsBaseError):
    """Raised when user profile operations fail."""
    pass


class AuthenticationError(AccountsBaseError):
    """Raised when authentication fails."""
    pass