import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_basic_imports():
    """Test that the basic modules can be imported without errors"""
    try:
        from config.settings import settings
        print("✓ Settings module imported successfully")
        
        # Check if all required environment variables are defined
        settings.validate()
        print("✓ Settings validation passed")
        
    except Exception as e:
        print(f"✗ Settings import failed: {str(e)}")
        return False

    try:
        from api.models import CallData, WebhookPayload
        print("✓ Models module imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {str(e)}")
        return False

    try:
        from utils.common import verify_webhook_signature, format_phone_number
        print("✓ Utils module imported successfully")
    except Exception as e:
        print(f"✗ Utils import failed: {str(e)}")
        return False

    print("All imports successful!")
    return True

if __name__ == "__main__":
    success = test_basic_imports()
    if not success:
        sys.exit(1)