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

# Add console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

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
            metadataHeaders=['From', 'Subject', 'References', 'In-Reply-To']
        ).execute()
        
        headers = message.get('payload', {}).get('headers', [])
        from_header = next((h for h in headers if h['name'] == 'From'), None)
        subject_header = next((h for h in headers if h['name'] == 'Subject'), None)
        references_header = next((h for h in headers if h['name'] == 'References'), None)
        in_reply_to_header = next((h for h in headers if h['name'] == 'In-Reply-To'), None)
        
        from_value = from_header['value'] if from_header else 'Unknown Sender'
        subject = subject_header['value'] if subject_header else 'No Subject'
        references = references_header['value'] if references_header else ''
        in_reply_to = in_reply_to_header['value'] if in_reply_to_header else ''
        
        # Extract email address from "Name <email@domain.com>" format
        email = from_value
        if '<' in from_value and '>' in from_value:
            email = from_value[from_value.find('<')+1:from_value.find('>')]
            
        return email, from_value, subject, references, in_reply_to
    except Exception as e:
        logging.error(f"Error getting email details from message {message_id}: {str(e)}")
        return None, None, None, None, None

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
        
        # Get list of active campaign email addresses and their thread IDs
        active_campaigns = df[df['Status'].isin(['Sent Email 1', 'Sent Email 2', 'Sent Email 3'])]
        
        if active_campaigns.empty:
            logging.info("No active campaign emails to check")
            return
        
        logging.info(f"Checking for replies from {len(active_campaigns)} active campaigns")
        logging.info(f"Active thread IDs: {active_campaigns['Thread ID'].tolist()}")
        
        # Get all messages from active campaign threads
        for thread_id in active_campaigns['Thread ID'].unique():
            if not thread_id:  # Skip empty thread IDs
                continue
                
            logging.info(f"Checking thread {thread_id}")
            try:
                thread = gmail_service.users().threads().get(userId='me', id=str(thread_id)).execute()
                messages = thread.get('messages', [])
                logging.info(f"Found {len(messages)} messages in thread")
                
                # Get the campaign details for this thread
                campaign = active_campaigns[active_campaigns['Thread ID'].astype(str) == str(thread_id)].iloc[0]
                recipient_email = campaign['Email Address']
                
                # Check each message in the thread
                for message in messages:
                    email, sender_name, subject, references, in_reply_to = get_email_address_from_message(gmail_service, message['id'])
                    logging.info(f"Message from: {email}, Subject: {subject}")
                    
                    # Skip if the message is from the sender email
                    if email == SENDER_EMAIL:
                        logging.info(f"Skipping message from sender: {email}")
                        continue
                    
                    # If we find a message from the recipient, it's a reply
                    if email == recipient_email or email == recipient_email.replace('@gmail.com', '@googlemail.com'):
                        logging.info(f"Found reply from {email} in thread {thread_id}")
                        
                        # Update campaign status
                        cell = worksheet.find(recipient_email)  # Search for the original recipient email
                        if cell:
                            current_status = worksheet.cell(cell.row, 5).value
                            if current_status != 'Reply Received':
                                worksheet.update_cell(cell.row, 5, 'Reply Received')
                                logging.info(f"Updated status for {recipient_email} to Reply Received")
                                
                                # Create Gmail link
                                gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{html.escape(message['id'])}"
                                
                                # Send Telegram notification
                                notification = (
                                    f"🔔 <b>New Reply Received!</b>\n\n"
                                    f"From: {html.escape(sender_name)}\n"
                                    f"Subject: {html.escape(subject)}\n"
                                    f"Status: Campaign status updated to 'Reply Received'\n\n"
                                    f"<a href='{gmail_link}'>View Email in Gmail</a>"
                                )
                                send_telegram_message(notification)
                                logging.info(f"Sent Telegram notification for reply from {email}")
                            else:
                                logging.info(f"Status already set to Reply Received for {recipient_email}")
                        break  # Stop checking messages once we find a reply
                        
            except Exception as e:
                logging.error(f"Error checking thread {thread_id}: {str(e)}")
                continue
    
    except Exception as e:
        error_msg = f"Error checking for replies: {str(e)}"
        logging.error(error_msg)
        send_telegram_message(f"⚠️ <b>Error in Reply Detection</b>\n\n{html.escape(error_msg)}")

if __name__ == "__main__":
    check_for_replies() 