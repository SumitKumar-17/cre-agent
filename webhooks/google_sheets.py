import os
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from api.models import CallData
from config.settings import settings

logger = logging.getLogger(__name__)

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_service():
    """Get authenticated Google Sheets service"""
    try:
        # Check if the credentials file exists
        if not os.path.exists(settings.GOOGLE_CREDENTIALS_FILE_PATH):
            raise FileNotFoundError(f"Google credentials file not found: {settings.GOOGLE_CREDENTIALS_FILE_PATH}")
        
        # Load credentials from service account file
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_FILE_PATH,
            scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error setting up Google Sheets service: {str(e)}")
        raise

def ensure_sheet_exists(service, spreadsheet_id: str, sheet_name: str):
    """Ensure the target sheet exists, create it if it doesn't"""
    try:
        # Get the spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        
        # Check if the sheet exists
        sheet_exists = any(sheet['properties']['title'] == sheet_name for sheet in sheets)
        
        if not sheet_exists:
            # Create the sheet
            request = {
                "addSheet": {
                    "properties": {
                        "title": sheet_name
                    }
                }
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [request]}
            ).execute()
            
            logger.info(f"Created new sheet: {sheet_name}")
            
            # Add headers to the new sheet
            add_headers_to_sheet(service, spreadsheet_id, sheet_name)
    except Exception as e:
        logger.error(f"Error ensuring sheet exists: {str(e)}")
        raise

def add_headers_to_sheet(service, spreadsheet_id: str, sheet_name: str):
    """Add headers to the sheet if it's empty"""
    try:
        range_name = f"{sheet_name}!A1:G1"
        headers = [["Timestamp", "Name", "Role", "Inquiry", "Market", "Phone", "Notes"]]
        
        body = {
            "values": headers
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()
        
        logger.info(f"Added headers to sheet: {sheet_name}")
    except Exception as e:
        logger.error(f"Error adding headers to sheet: {str(e)}")
        raise

def log_call_to_sheet(call_data: CallData):
    """
    Log call data to Google Sheets
    """
    try:
        # Get Google Sheets service
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        
        # Ensure the 'Calls' sheet exists
        ensure_sheet_exists(service, settings.GOOGLE_SHEET_ID, 'Calls')
        
        # Prepare the data to append to the sheet
        values = [
            [
                call_data.timestamp or "N/A",
                call_data.name or "N/A",
                call_data.role or "N/A",
                call_data.inquiry or "N/A",
                call_data.market or "N/A", 
                call_data.phone_number or "N/A",
                call_data.notes or "N/A"
            ]
        ]
        
        # Specify the range where data will be added
        range_name = 'Calls!A2:G'  # Start from row 2 to skip headers
        
        # Append the data to the sheet
        body = {
            'values': values
        }
        
        result = sheet.values().append(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',  # This interprets numbers and dates properly
            body=body
        ).execute()
        
        rows_added = result.get('updates', {}).get('updatedRows', 0)
        logger.info(f"Call data successfully logged to Google Sheets. {rows_added} row(s) added.")
        
    except Exception as e:
        logger.error(f"Error logging call to Google Sheets: {str(e)}")
        # In a production environment, you might want to store failed logs in a queue
        # to retry later or send an alert
        raise