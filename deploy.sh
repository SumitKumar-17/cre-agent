#!/bin/bash

# Deployment script for CRE AI Agent
set -e  # Exit on any error

echo "Starting deployment of CRE AI Agent..."

# Check if running in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Source environment variables
export $(grep -v '^#' .env | xargs)

# Validate required environment variables
if [ -z "$VAPI_API_KEY" ]; then
    echo "Error: VAPI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$GOOGLE_SHEET_ID" ] || [ -z "$GOOGLE_CREDENTIALS_FILE_PATH" ]; then
    echo "Error: Google Sheets configuration not complete in .env file"
    exit 1
fi

echo "Environment variables validated."

# Run tests to ensure everything works
echo "Running tests..."
pytest tests/ -v

if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix the issues before deployment."
    exit 1
fi

echo "Tests passed."

# Check if webhook URL is set
if [ -z "$WEBHOOK_URL" ]; then
    echo "Warning: WEBHOOK_URL not set. The webhook will not work until this is configured."
    echo "Please update your .env file with the correct webhook URL."
fi

# Display deployment information
echo ""
echo "==============================================="
echo "CRE AI Agent Deployment Complete!"
echo "==============================================="
echo ""
echo "Application Information:"
echo "- Brokerage: Mid-Tier CRE Solutions"
echo "- Environment: $APP_ENV"
echo "- Port: $PORT"
echo "- Webhook URL: $WEBHOOK_URL"
echo ""
echo "Next Steps:"
echo "1. Ensure your webhook URL is publicly accessible"
echo "2. Configure your Vapi assistant with the webhook URL"
echo "3. Set up your phone number through Vapi/Twilio"
echo "4. Verify Google Sheets integration is working"
echo "5. Test with a phone call to your assigned number"
echo ""
echo "To run the application:"
echo "  uvicorn main:app --host 0.0.0.0 --port $PORT"
echo ""
echo "To run the dashboard:"
echo "  streamlit run ui/dashboard.py"
echo ""
echo "==============================================="

# Ask if user wants to start the application
read -p "Do you want to start the application now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting CRE AI Agent application..."
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload &
    
    echo "Starting dashboard..."
    streamlit run ui/dashboard.py &
    
    echo "Applications started in background."
    echo "Main API: http://localhost:$PORT"
    echo "Dashboard: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop both applications."
    
    # Wait for user to press Ctrl+C
    wait
fi