from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class CallData(BaseModel):
    """Model for the call data received from Vapi"""
    timestamp: str
    name: Optional[str] = None
    role: Optional[str] = None  # property_owner, buyer, lender, general_inquiry
    inquiry: Optional[str] = None
    market: Optional[str] = None
    notes: Optional[str] = None
    phone_number: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    call_result: Optional[str] = None  # success, missed, etc.


class WebhookPayload(BaseModel):
    """Model for the webhook payload from Vapi"""
    type: str  # "call-start", "call-end", "conversation-update", etc.
    callId: str
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    transcript: Optional[List[Dict[str, Any]]] = None
    recordingUrl: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    callerIdNumber: Optional[str] = None
    callerIdName: Optional[str] = None
    callStatus: Optional[str] = None