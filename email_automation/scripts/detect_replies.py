import base64
import logging
from datetime import datetime, timedelta
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import html

from ..config.config import *
from ..utils.telegram_notifier import send_telegram_message

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename=ERROR_LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_gmail_service():
    """Initialize and return Gmail API service using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=GMAIL_SCOPES
        )
        
        # Create delegated credentials
        delegated_credentials = credentials.with_subject(SENDER_EMAIL)
        
        return build('gmail', 'v1', credentials=delegated_credentials)
    except Exception as e:
        logging.error(f"Error setting up Gmail service: {str(e)}")
        return None

def get_sheets_client():
    """Initialize and return Google Sheets client."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(credentials)

def get_email_address_from_message(service, message_id):
    """Extract sender's email address from a message."""
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['From', 'Subject']
        ).execute()
        
        headers = message.get('payload', {}).get('headers', [])
        from_header = next((h for h in headers if h['name'] == 'From'), None)
        subject_header = next((h for h in headers if h['name'] == 'Subject'), None)
        
        from_value = from_header['value'] if from_header else 'Unknown Sender'
        subject = subject_header['value'] if subject_header else 'No Subject'
        
        # Extract email address from "Name <email@domain.com>" format
        email = from_value
        if '<' in from_value and '>' in from_value:
            email = from_value[from_value.find('<')+1:from_value.find('>')]
            
        return email, from_value, subject
    except Exception as e:
        logging.error(f"Error getting email details from message {message_id}: {str(e)}")
        return None, None, None

def check_for_replies():
    """Check Gmail inbox for replies from campaign recipients."""
    try:
        # Initialize services
        gmail_service = get_gmail_service()
        if not gmail_service:
            logging.error("Failed to initialize Gmail service")
            return
            
        sheets_client = get_sheets_client()
        
        # Open spreadsheet and get campaign data
        spreadsheet = sheets_client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # Get list of active campaign email addresses
        active_emails = df[df['Status'].isin(['Sent Email 1', 'Sent Email 2', 'Sent Email 3'])]['Email Address'].tolist()
        
        if not active_emails:
            logging.info("No active campaign emails to check")
            return
        
        # Search for replies in the last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        query = f'after:{yesterday}'
        
        results = gmail_service.users().messages().list(
            userId='me',
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        for message in messages:
            email, sender_name, subject = get_email_address_from_message(gmail_service, message['id'])
            
            if email in active_emails:
                # Update campaign status
                cell = worksheet.find(email)
                if cell:
                    worksheet.update_cell(cell.row, 5, 'Reply Received')
                    logging.info(f"Reply received from {email}")
                    
                    # Create Gmail link - escape special characters
                    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{html.escape(message['id'])}"
                    
                    # Send Telegram notification with escaped values
                    notification = (
                        f"🔔 <b>New Reply Received!</b>\n\n"
                        f"From: {html.escape(sender_name)}\n"
                        f"Subject: {html.escape(subject)}\n"
                        f"Status: Campaign status updated to 'Reply Received'\n\n"
                        f"<a href='{gmail_link}'>View Email in Gmail</a>"
                    )
                    send_telegram_message(notification)
    
    except Exception as e:
        error_msg = f"Error checking for replies: {str(e)}"
        logging.error(error_msg)
        send_telegram_message(f"⚠️ <b>Error in Reply Detection</b>\n\n{html.escape(error_msg)}")

if __name__ == "__main__":
    check_for_replies() 