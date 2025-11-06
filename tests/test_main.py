import pytest
from fastapi.testclient import TestClient
from main import app
from api.models import CallData
from webhooks.google_sheets import log_call_to_sheet
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CRE AI Agent is running"
    assert data["status"] == "active"


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_vapi_webhook_call_start():
    """Test Vapi webhook for call start event"""
    payload = {
        "type": "call-start",
        "callId": "test-call-id-123",
        "startTime": "2023-10-01T12:00:00Z",
        "callerIdNumber": "+15551234567",
        "callerIdName": "Test Caller"
    }
    
    response = client.post("/webhook/vapi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"


def test_vapi_webhook_call_end():
    """Test Vapi webhook for call end event"""
    payload = {
        "type": "call-end",
        "callId": "test-call-id-123",
        "startTime": "2023-10-01T12:00:00Z",
        "endTime": "2023-10-01T12:10:00Z",
        "callerIdNumber": "+15551234567",
        "callerIdName": "Test Caller",
        "callStatus": "completed",
        "transcript": [
            {"role": "assistant", "message": "Hello! Thank you for calling Mid-Tier CRE Solutions."},
            {"role": "user", "message": "Hi, I'm looking to buy an office building."}
        ]
    }
    
    response = client.post("/webhook/vapi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"


@patch('webhooks.google_sheets.get_google_sheets_service')
def test_log_call_to_sheet_success(mock_service):
    """Test logging call data to Google Sheets"""
    # Mock the Google Sheets service
    mock_spreadsheet = MagicMock()
    mock_values = MagicMock()
    mock_service.return_value.spreadsheets.return_value = mock_spreadsheet
    mock_spreadsheet.values.return_value = mock_values
    
    # Create test call data
    call_data = CallData(
        timestamp="2023-10-01T12:00:00Z",
        name="Test Caller",
        role="buyer",
        inquiry="Looking for office space",
        market="Downtown",
        notes="Interested in 5000 sq ft space"
    )
    
    # This should not raise an exception
    log_call_to_sheet(call_data)
    
    # Verify that the append method was called
    assert mock_values.append.called


if __name__ == "__main__":
    pytest.main()