"""
Enhanced Dashboard UI for CRE Agent - using Streamlit
"""
import streamlit as st
import pandas as pd
import json
import datetime
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from config.settings import settings
import time


def get_google_sheets_data():
    """
    Fetch data from Google Sheets
    """
    try:
        if not settings.GOOGLE_SHEET_ID or not settings.GOOGLE_CREDENTIALS_FILE_PATH:
            st.warning("Google Sheets configuration not found. Please set up your .env file.")
            return pd.DataFrame()
        
        # Load credentials from service account file
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_FILE_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        # Get data from the 'Calls' sheet
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range='Calls!A1:G'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.info("No data found in the Google Sheet.")
            return pd.DataFrame()
        
        # Create DataFrame from the sheet data
        headers = values[0]
        data = values[1:] if len(values) > 1 else []
        
        df = pd.DataFrame(data, columns=headers)
        return df
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {str(e)}")
        st.info("Make sure you have properly set up your Google Sheets credentials in the .env file.")
        return pd.DataFrame()


def create_role_distribution_chart(df):
    """Create a chart showing distribution of caller roles"""
    if 'Role' in df.columns:
        role_counts = df['Role'].value_counts()
        fig = px.pie(
            values=role_counts.values, 
            names=role_counts.index,
            title="Caller Type Distribution",
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        return fig
    return None


def create_timeline_chart(df):
    """Create a timeline chart showing call volume over time"""
    if 'Timestamp' in df.columns:
        # Convert timestamp to datetime for analysis
        df_copy = df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Timestamp'], errors='coerce')
        df_copy = df_copy.dropna(subset=['Date'])
        
        # Group by date and count
        daily_calls = df_copy.groupby(df_copy['Date'].dt.date).size().reset_index(name='Count')
        
        if not daily_calls.empty:
            fig = px.line(
                daily_calls,
                x='Date',
                y='Count',
                title="Call Volume Over Time",
                markers=True,
                line_shape='linear'
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Calls"
            )
            return fig
    return None


def create_heatmap_chart(df):
    """Create a heatmap of call patterns"""
    if 'Role' in df.columns and 'Timestamp' in df.columns:
        df_copy = df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Timestamp'], errors='coerce')
        df_copy = df_copy.dropna(subset=['Date'])
        df_copy['Hour'] = df_copy['Date'].dt.hour
        df_copy['Day'] = df_copy['Date'].dt.day_name()
        
        # Group by day and hour
        heatmap_data = df_copy.groupby(['Day', 'Hour']).size().unstack(fill_value=0)
        
        if not heatmap_data.empty:
            fig = px.imshow(
                heatmap_data,
                title="Call Activity Heatmap",
                color_continuous_scale='Blues',
                aspect="auto"
            )
            return fig
    return None


def main():
    """
    Main dashboard function with enhanced UI
    """
    st.set_page_config(
        page_title="CRE Agent Dashboard",
        page_icon="🏢",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #70ad47;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    .data-table {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">🏢 CRE AI Agent Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Call tracking and analytics for commercial real estate brokerage</div>', unsafe_allow_html=True)
    
    # Initialize session state for auto-refresh
    if 'refresh_counter' not in st.session_state:
        st.session_state.refresh_counter = 0
    
    # Sidebar with filters and controls
    with st.sidebar:
        st.header("🔍 Filters & Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, 60)
            st.session_state.refresh_counter += 1
            time.sleep(refresh_interval)
            st.rerun()
        
        # Date range filter
        date_range = st.date_input(
            "Select date range",
            value=(datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()),
            key="date_range"
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.session_state.refresh_counter += 1
            st.rerun()
        
        # System status
        with st.expander("⚙️ System Status"):
            st.json({
                "Environment": settings.APP_ENV,
                "Port": settings.PORT,
                "Google Sheet ID": settings.GOOGLE_SHEET_ID if settings.GOOGLE_SHEET_ID else "Not configured",
                "VAPI API Key": "Configured" if settings.VAPI_API_KEY else "Not configured"
            })
    
    # Load data
    df = get_google_sheets_data()
    
    # Main content area
    if df.empty:
        st.info("### 📊 No call data available")
        st.markdown("""
        The dashboard will show data once calls are logged to Google Sheets.
        
        To start receiving calls:
        1. Deploy your application to a public URL
        2. Configure Vapi with your webhook URL
        3. Set up your phone number through Vapi/Twilio
        """)
        
        # Display setup instructions
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            ### Setting up your CRE AI Agent:
            
            1. **Configure environment variables** in your `.env` file:
               - Set your Vapi API key
               - Configure Google Sheets credentials
               - Set your webhook URL
            
            2. **Deploy your application**:
               - Use a platform like Render, Heroku, or AWS
               - Ensure your webhook endpoint is publicly accessible
            
            3. **Configure Vapi**:
               - Create an assistant in the Vapi dashboard
               - Set the webhook URL to your deployed endpoint
               - Assign a phone number
            
            4. **Test the system**:
               - Call your assigned phone number
               - Verify calls are logged in Google Sheets
            """)
        
        return
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_calls = len(df)
    unique_callers = df['Name'].nunique() if 'Name' in df.columns else 0
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Calls", total_calls)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Unique Callers", unique_callers)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        if 'Role' in df.columns:
            unique_roles = df['Role'].nunique()
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Caller Types", unique_roles)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Caller Types", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Last Updated", datetime.datetime.now().strftime("%H:%M:%S"))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts and analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # Role distribution chart
        role_chart = create_role_distribution_chart(df)
        if role_chart:
            st.plotly_chart(role_chart, use_container_width=True)
        else:
            st.info("Role data not available for charting")
    
    with col2:
        # Timeline chart
        timeline_chart = create_timeline_chart(df)
        if timeline_chart:
            st.plotly_chart(timeline_chart, use_container_width=True)
        else:
            st.info("Timeline data not available for charting")
    
    # Heatmap chart
    heatmap_chart = create_heatmap_chart(df)
    if heatmap_chart:
        st.plotly_chart(heatmap_chart, use_container_width=True)
    else:
        st.info("Activity data not sufficient for heatmap")
    
    # Call log table
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.subheader("📋 Recent Call Log")
    
    # Show the raw data table with some formatting
    if not df.empty:
        # Format the dataframe for better display
        display_df = df.copy()
        if 'Timestamp' in display_df.columns:
            display_df['Timestamp'] = pd.to_datetime(display_df['Timestamp'], errors='coerce')
        
        # Apply date filter if dates are selected
        if len(date_range) == 2 and all(date_range):
            start_date, end_date = date_range
            if 'Timestamp' in display_df.columns:
                display_df = display_df[
                    (display_df['Timestamp'].dt.date >= start_date) & 
                    (display_df['Timestamp'].dt.date <= end_date)
                ]
        
        # Display the table
        st.dataframe(display_df, use_container_width=True, height=500)
    else:
        st.info("No call data to display.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export functionality
    if st.button("📥 Export Current Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"cre_calls_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )


if __name__ == "__main__":
    main()