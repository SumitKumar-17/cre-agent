from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.settings import settings
from api.models import WebhookPayload, CallData
from agents.cre_agent import handle_inbound_call
from webhooks.google_sheets import log_call_to_sheet
from typing import Optional
from datetime import datetime
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CRE AI Agent",
    description="AI agent for commercial real estate brokerage",
    version="1.0.0"
)

# Mount static files if UI directory exists
ui_path = os.path.join(os.path.dirname(__file__), "ui")
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html=True), name="ui")

# Templates for HTML responses if needed
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting CRE AI Agent application")
    settings.validate()  # Validate required environment variables
    logger.info("Environment variables validated")


@app.get("/")
async def root():
    """Root endpoint to check if the service is running"""
    return {
        "message": "CRE AI Agent is running",
        "status": "active",
        "brokerage": "Mid-Tier CRE Solutions",
        "endpoints": {
            "webhook": "/webhook/vapi",
            "dashboard": "/dashboard",
            "health": "/health",
            "api": "/docs"
        }
    }


@app.get("/dashboard")
async def dashboard():
    """Redirect to the Streamlit dashboard"""
    return {"message": "Dashboard available at /ui/dashboard or run streamlit ui/dashboard.py"}


@app.post("/webhook/vapi")
async def vapi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for Vapi call events
    Receives call data and logs it to Google Sheets
    """
    try:
        # Verify webhook signature if needed
        payload = await request.json()
        logger.info(f"Received webhook: {payload.get('type', 'unknown')} for call {payload.get('callId', 'unknown')}")
        
        # Parse the webhook payload
        try:
            webhook_data = WebhookPayload(**payload)
        except Exception as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        
        # Handle different webhook types
        if webhook_data.type == "call-start":
            logger.info(f"Call started: {webhook_data.callId}")
            # Could start call processing here if needed
            
        elif webhook_data.type == "call-end":
            logger.info(f"Call ended: {webhook_data.callId}")
            
            # Extract call data for logging to Google Sheets
            call_data = extract_call_data(webhook_data)
            
            # Process in background to avoid webhook timeout
            background_tasks.add_task(log_call_to_sheet, call_data)
            
        elif webhook_data.type == "conversation-update":
            logger.info(f"Conversation update: {webhook_data.callId}")
            # Handle conversation updates if needed
        
        return JSONResponse(content={"status": "received"}, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


def extract_call_data(webhook_payload: WebhookPayload) -> CallData:
    """
    Extract relevant call data from webhook payload
    """
    # This is a simplified extraction - in a real implementation, 
    # you might analyze the transcript to determine role, inquiry, etc.
    call_data = CallData(
        timestamp=webhook_payload.endTime or webhook_payload.startTime or "",
        phone_number=webhook_payload.callerIdNumber,
        name=webhook_payload.callerIdName,
        duration=None,  # Would need to calculate from start/end times
        call_result=webhook_payload.callStatus
    )
    
    # In a real implementation, analyze transcript to extract:
    # - Role (property owner, buyer, lender, general inquiry)
    # - Inquiry details (property type, location, budget, etc.)
    # - Market (geographic area, property type)
    # - Notes (key points from conversation)
    
    if webhook_payload.transcript:
        # Analyze the transcript to extract more detailed information
        from agents.cre_agent import cre_agent
        qualification = cre_agent.qualify_caller(webhook_payload.transcript)
        
        call_data.role = qualification.get("caller_type", "unknown")
        call_data.inquiry = qualification.get("key_points", ["No specific inquiry identified"])[0] if qualification.get("key_points") else "No specific inquiry identified"
        call_data.market = qualification.get("location_interest", "unknown")
        call_data.notes = f"Interest Level: {qualification.get('interest_level', 'unknown')}, Property Type: {qualification.get('property_type', 'unknown')}, Budget: {qualification.get('budget_range', 'unknown')}"
    
    return call_data


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cre-agent", "timestamp": str(datetime.utcnow())}


# API endpoint to get recent calls data (for dashboard)
@app.get("/api/calls")
async def get_recent_calls(limit: int = 10):
    """Get recent calls data - simplified implementation"""
    # In a real implementation, you'd fetch from database or Google Sheets
    # For now, return a placeholder response
    return {"message": "This endpoint would return recent calls data. Currently, data is stored in Google Sheets."}


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=settings.PORT, 
        reload=settings.APP_ENV == "development"
    )