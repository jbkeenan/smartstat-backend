from typing import Optional

class VendorError(Exception):
    def __init__(self, vendor: str, message: str, code: Optional[str] = None, status: int = 502):
        super().__init__(message)
        self.vendor = vendor
        self.message = message
        self.code = code
        self.status = status

    def to_response(self):
        return {
            "vendor": self.vendor,
            "error": self.code or "vendor_error",
            "message": self.message,
        }, self.status
