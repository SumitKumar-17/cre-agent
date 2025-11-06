import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the CRE AI Agent"""
    
    # Vapi Configuration
    VAPI_API_KEY: str = os.getenv("VAPI_API_KEY", "")
    
    # Google Sheets Configuration
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_CREDENTIALS_FILE_PATH: str = os.getenv("GOOGLE_CREDENTIALS_FILE_PATH", "")
    
    # App Configuration
    APP_ENV: str = os.getenv("APP_ENV", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    
    # Validation
    @classmethod
    def validate(cls):
        required_vars = [
            "VAPI_API_KEY",  # This is required for production
        ]
        
        # Only check if needed for testing
        if cls.APP_ENV == "production":
            missing_vars = []
            for var in required_vars:
                if not getattr(cls, var):
                    missing_vars.append(var)
            
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @classmethod
    def is_production(cls) -> bool:
        return cls.APP_ENV.lower() == "production"

# Create a global settings instance
settings = Settings()