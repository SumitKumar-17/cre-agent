# CRE AI Agent for Commercial Real Estate Brokerage

## Overview
This project implements a comprehensive AI call agent for mid-tier commercial real estate (CRE) brokerages. The agent handles inbound calls from property owners, buyers, lenders, and general inquiries, qualifying callers and logging all interactions to Google Sheets for follow-up. Features include natural voice interactions using Vapi and Cartesia Sonic 3, real-time data logging, and a comprehensive dashboard for monitoring.

## Features
- Natural, expressive voice interactions using Vapi and Cartesia Sonic 3
- Intelligent call qualification for property owners, buyers, lenders, and general inquiries
- Automatic logging of call data to Google Sheets with timestamp, name, role, inquiry, market, and notes
- Real-time webhook integration for processing call events
- Interactive dashboard for monitoring call analytics
- Modular, well-documented codebase following best practices

## Project Structure
```
cre-agent/
├── agents/                 # AI agent logic and call handling
│   └── cre_agent.py        # Main CRE agent implementation
├── api/                    # API models and endpoints
│   └── models.py           # Pydantic models for data validation
├── config/                 # Configuration management
│   └── settings.py         # Environment and app settings
├── ui/                     # Dashboard interface
│   └── dashboard.py        # Streamlit dashboard
├── utils/                  # Utility functions
│   └── common.py           # Helper functions
├── webhooks/               # Webhook handlers
│   └── google_sheets.py    # Google Sheets integration
├── tests/                  # Test suite
├── deploy.sh               # Deployment script
├── setup.sh                # Setup script
├── main.py                 # Main application entrypoint
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── IMPLEMENTATION.md       # Comprehensive documentation
└── README.md              # Project documentation
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Vapi account and API key
- Google Sheets API credentials
- Cartesia API key (for Sonic 3 voice)

### Automated Setup
1. Run the setup script:
```bash
./setup.sh
```

### Manual Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. For development, install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

## Environment Variables
Create a `.env` file with the following variables:

```
# Vapi API Configuration
VAPI_API_KEY=your_vapi_api_key_here

# Google Sheets Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_CREDENTIALS_FILE_PATH=path_to_your_google_credentials_file

# Cartesia Configuration
CARTESIA_API_KEY=your_cartesia_api_key

# App Configuration
APP_ENV=development
PORT=8000
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_URL=https://yourdomain.com/webhook/vapi
```

## API Keys Required
- **Vapi API Key**: For call management and webhook handling
- **Google Sheets API credentials**: For logging call data
- **Cartesia API Key**: For Sonic 3 voice synthesis

## Running the Application
### Development
```bash
# Start the main API server
uvicorn main:app --reload

# Start the dashboard separately
streamlit run ui/dashboard.py
```

### Production
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Testing
Run tests with pytest:
```bash
pytest tests/
```

## Dashboard
The application includes a comprehensive dashboard built with Streamlit:
- Access at: `http://localhost:8501` when running `streamlit run ui/dashboard.py`
- Shows real-time call analytics
- Displays caller type distribution charts
- Provides call volume over time analysis
- Includes filtering and data export functionality

## Configuration Notes
- Use Vapi for call management and webhook handling
- Use Cartesia Sonic 3 for natural, expressive voice interactions
- Use Google Sheets for call data logging
- Ensure webhook endpoints are publicly accessible for Vapi integration
- The application listens for call events from Vapi via webhooks at `/webhook/vapi`

## Call Flow
1. Inbound calls are received by Vapi
2. The AI agent engages with the caller using natural language with Cartesia Sonic 3 voice
3. The conversation is analyzed to determine caller type (property owner, buyer, lender, etc.)
4. Call data is extracted including timestamp, name, role, inquiry, market, and notes
5. Data is logged to Google Sheets in the background to avoid webhook timeouts
6. Brokers can review logged calls via the dashboard for follow-up

## Integration with Vapi
- Set up your Vapi account and create an assistant
- Configure the assistant to use Cartesia Sonic 3 voice
- Set the webhook URL to your deployed application's `/webhook/vapi` endpoint
- Assign a phone number through Vapi/Twilio
- Configure the assistant with the CRE-specific system prompt

## Google Sheets Setup
1. Create a Google Sheet with appropriate permissions
2. Set up Google Sheets API credentials (service account)
3. Share the sheet with the service account email
4. Update the `GOOGLE_SHEET_ID` and `GOOGLE_CREDENTIALS_FILE_PATH` in your `.env` file
5. The sheet will automatically be created with headers if it doesn't exist

The application will create the following columns in the "Calls" sheet:
- Timestamp
- Name
- Role (property_owner, buyer, lender, general_inquiry)
- Inquiry
- Market
- Phone
- Notes

## Brokerage: Mid-Tier CRE Solutions
This solution is designed for mid-tier commercial real estate brokerages, providing an AI assistant that can handle a variety of inbound calls and qualify prospects efficiently. The system helps brokerages manage their inbound calls without requiring a full-time receptionist.

## Deployment
For production deployment:
1. Deploy the FastAPI application to a cloud provider (Heroku, Render, AWS, etc.)
2. Ensure the webhook endpoint is publicly accessible
3. Update the `WEBHOOK_URL` in your environment variables
4. Configure a phone number through Vapi
5. Set up the Google Sheets integration
6. Test the complete call flow

## Security
- All API keys are stored in environment variables
- Follow Google Cloud security best practices for service account keys
- Consider implementing webhook signature verification for added security

For comprehensive technical documentation, see [IMPLEMENTATION.md](IMPLEMENTATION.md).
