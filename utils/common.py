import hashlib
import hmac
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify the webhook signature to ensure it comes from a trusted source
    """
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


def format_phone_number(phone: str) -> str:
    """
    Format phone number to a standard format
    """
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Format as (XXX) XXX-XXXX if it's a US number
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return f"(+{digits_only[0]}) ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    else:
        return phone  # Return as-is if not a standard format


def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and normalizing
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = ' '.join(text.split())
    return cleaned


def extract_email(text: str) -> str:
    """
    Extract email from text (simplified implementation)
    """
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""


def extract_location(text: str) -> str:
    """
    Extract location from text (simplified implementation)
    In a production system, you'd use NER (Named Entity Recognition)
    """
    # This is a simplified implementation
    # In reality, you'd use libraries like spaCy or transformers for NER
    
    # Common city/region indicators in commercial real estate
    location_keywords = [
        "downtown", "midtown", "uptown", "suburb", "metro", "city", 
        "district", "area", "zone", "region", "neighborhood", "business district",
        # Add specific location names relevant to your market
        "manhattan", "brooklyn", "queens", "bronx", "staten island",
        "downtown", "financial district", "midtown", "uptown", "soho", "tribeca"
    ]
    
    text_lower = text.lower()
    found_locations = [kw for kw in location_keywords if kw in text_lower]
    
    return ", ".join(found_locations) if found_locations else "unknown"