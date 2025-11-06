import asyncio
from vapi_python import Vapi
from config.settings import settings
import logging
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class CREAgent:
    """Main AI agent for handling CRE calls"""
    
    def __init__(self):
        self.vapi: Optional[Vapi] = None
        self.active_calls = {}
        self.initialize_vapi()
    
    def initialize_vapi(self):
        """Initialize the Vapi client"""
        try:
            self.vapi = Vapi(api_key=settings.VAPI_API_KEY)
            logger.info("Vapi client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vapi: {str(e)}")
            raise
    
    def get_caller_type(self, initial_context: str) -> str:
        """
        Determine caller type based on initial context using simple keyword matching
        In a production system, this would use more sophisticated NLP
        """
        if not initial_context:
            return "general_inquiry"
            
        context_lower = initial_context.lower()
        
        if any(keyword in context_lower for keyword in ["property", "own", "landlord", "building", "lease", "rent", "my property"]):
            return "property_owner"
        elif any(keyword in context_lower for keyword in ["buy", "purchase", "investor", "looking", "acquire", "investment", "buying"]):
            return "buyer"
        elif any(keyword in context_lower for keyword in ["lend", "loan", "finance", "mortgage", "credit", "financing"]):
            return "lender"
        else:
            return "general_inquiry"
    
    def create_assistant_config(self) -> Dict[str, Any]:
        """
        Create the assistant configuration with Cartesia Sonic 3 voice
        """
        assistant_config = {
            "model": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "systemPrompt": """You are an AI assistant for Mid-Tier CRE Solutions, a commercial real estate brokerage. Your role is to understand the caller's needs, qualify them as a property owner, buyer, lender, or general inquiry, and collect relevant information. Be friendly, professional, and conversational. Ask follow-up questions to better understand their needs. If possible, schedule a consultation with a broker. Focus on gathering information about:
                - Property type they're interested in (office, retail, industrial, etc.)
                - Location preferences
                - Timeline for their project
                - Budget or price range
                - Contact information for follow-up"""
            },
            "firstMessage": "Hello! Thank you for calling Mid-Tier CRE Solutions, a commercial real estate brokerage. How can I assist you today?",
            "endCallFunctionEnabled": True,
            "voicemailDetectionEnabled": True,
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2-conversationalai"
            },
            "voice": {
                "provider": "cartesia",
                "voiceId": "sonic-3",  # Using Cartesia Sonic 3 as requested
                "model": "sonic-3"
            },
            "silenceTimeoutSeconds": 15,
            "responseDelay": 0.2,
        }
        
        # Add webhook URL if available
        if settings.WEBHOOK_URL:
            assistant_config["serverUrl"] = settings.WEBHOOK_URL
        
        return assistant_config
    
    def create_assistant(self) -> str:
        """
        Create an assistant in Vapi with the CRE-specific configuration
        """
        try:
            assistant_config = self.create_assistant_config()
            
            # Create the assistant using Vapi's API
            # Note: The exact API calls may vary depending on the Vapi SDK version
            assistant_response = self.vapi.create_assistant(assistant_config)
            assistant_id = assistant_response['id'] if isinstance(assistant_response, dict) else getattr(assistant_response, 'id', None)
            
            logger.info(f"Created assistant with ID: {assistant_id}")
            return assistant_id
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            raise
    
    def start_call(self, assistant_id: str, phone_number: str) -> Dict[str, Any]:
        """
        Start a phone call with the Vapi assistant
        """
        try:
            call_config = {
                "assistantId": assistant_id,
                "number": phone_number,
                "type": "outbound"
            }
            
            # Start the call
            call_response = self.vapi.create_call(call_config)
            call_id = call_response['id'] if isinstance(call_response, dict) else getattr(call_response, 'id', None)
            
            logger.info(f"Started call with ID: {call_id}")
            return {"call_id": call_id, "status": "started"}
        except Exception as e:
            logger.error(f"Error starting call: {str(e)}")
            raise
    
    def qualify_caller(self, transcript: list) -> dict:
        """
        Qualify the caller based on conversation transcript
        Returns a dictionary with qualification details
        """
        qualification = {
            "caller_type": "unknown",
            "interest_level": "low",  # low, medium, high
            "urgency": "low",  # low, medium, high
            "budget_range": "unknown",
            "property_type": "unknown",
            "location_interest": "unknown",
            "contact_info": "unknown",
            "key_points": []
        }
        
        if transcript:
            # Analyze the transcript to extract qualification details
            all_text = " ".join([item.get("message", "") if isinstance(item, dict) else str(item) for item in transcript if item])
            
            # Determine caller type
            qualification["caller_type"] = self.get_caller_type(all_text)
            
            # Determine interest level based on engagement
            words = all_text.lower().split()
            interested_keywords = ["definitely", "absolutely", "yes", "interested", "looking", "ready", "now", "today", "immediately"]
            urgent_keywords = ["urgent", "asap", "immediately", "soon", "right away", "this week", "today"]
            
            interest_matches = [word for word in words if word in interested_keywords]
            urgency_matches = [word for word in words if word in urgent_keywords]
            
            qualification["interest_level"] = "high" if len(interest_matches) > 2 else "medium" if len(interest_matches) > 0 else "low"
            qualification["urgency"] = "high" if len(urgency_matches) > 1 else "medium" if len(urgency_matches) > 0 else "low"
            
            # Extract other details
            # This is a simplified implementation - in reality, you'd use more sophisticated NLP
            if any(word in all_text.lower() for word in ["office", "medical office", "office building"]):
                qualification["property_type"] = "office"
            elif any(word in all_text.lower() for word in ["retail", "shop", "store", "restaurant"]):
                qualification["property_type"] = "retail"
            elif any(word in all_text.lower() for word in ["industrial", "warehouse", "manufacturing", "distribution"]):
                qualification["property_type"] = "industrial"
            elif "warehouse" in all_text.lower():
                qualification["property_type"] = "warehouse"
            elif any(word in all_text.lower() for word in ["land", "lot", "parcel"]):
                qualification["property_type"] = "land"
            elif any(word in all_text.lower() for word in ["apartment", "residential", "multi-family"]):
                qualification["property_type"] = "residential"
            
            # Look for location mentions (simplified)
            # In a real implementation, you'd use NER to identify locations
            location_indicators = ["near", "in", "around", "downtown", "uptown", "suburb", "area", "district", "city", "town"]
            for indicator in location_indicators:
                if indicator in all_text.lower():
                    # In a real implementation, you'd extract the actual location name
                    qualification["location_interest"] = "identified"
                    break
            else:
                qualification["location_interest"] = "not_specified"
            
            # Look for budget mentions (simplified)
            # In a real implementation, you'd extract numerical values with context
            budget_indicators = ["budget", "range", "price", "cost", "value", "$"]
            for indicator in budget_indicators:
                if indicator in all_text.lower():
                    # In a real implementation, you'd extract the actual budget
                    qualification["budget_range"] = "identified"
                    break
            else:
                qualification["budget_range"] = "not_specified"
            
            # Extract key points from the conversation
            key_point_indicators = [
                "my budget is", "looking for", "need", "want", "plan to", "looking to", 
                "interested in", "property with", "require", "need space for"
            ]
            
            for item in transcript:
                if isinstance(item, dict) and "message" in item:
                    message = item["message"].lower()
                    for indicator in key_point_indicators:
                        if indicator in message:
                            qualification["key_points"].append(item["message"])
                            break
        
        return qualification


# Global instance of the CRE Agent
cre_agent = CREAgent()


def handle_inbound_call(caller_info: dict):
    """
    Public function to handle inbound calls
    """
    # The actual call handling needs to be done via Vapi's webhook system
    # This function would be triggered when Vapi sends a webhook
    logger.info(f"Handling inbound call from {caller_info.get('phoneNumber', 'unknown')}")
    return {"status": "inbound call received", "caller_info": caller_info}