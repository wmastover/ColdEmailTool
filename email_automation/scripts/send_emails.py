import os
import base64
import logging
import json
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

from ..config.config import *

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Validate environment variables
if not SENDER_EMAIL:
    raise ValueError("SENDER_EMAIL environment variable is not set")
if not SENDER_NAME:
    raise ValueError("SENDER_NAME environment variable is not set")

logging.info(f"Starting email automation with sender: {SENDER_EMAIL}")

def get_gmail_service():
    """Initialize and return Gmail API service using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=GMAIL_SCOPES,
            subject=SENDER_EMAIL
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Test the connection
        profile = service.users().getProfile(userId='me').execute()
        logging.info(f"Successfully connected to Gmail API as: {profile.get('emailAddress')}")
        return service
    except Exception as e:
        logging.error(f"Error setting up Gmail service: {str(e)}")
        return None

def get_sheets_client():
    """Initialize and return Google Sheets client."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SHEETS_SCOPES
        )
        client = gspread.authorize(credentials)
        logging.info("Successfully connected to Google Sheets API")
        return client
    except Exception as e:
        logging.error(f"Error setting up Sheets client: {str(e)}")
        return None

def load_email_template(template_name):
    """Load email template from file."""
    template_path = TEMPLATE_DIR / template_name
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Split subject and body
    lines = content.split('\n')
    subject = lines[0].replace('Subject: ', '')
    body = '\n'.join(lines[2:])
    
    # Replace sender name placeholder
    body = body.replace('{sender_name}', SENDER_NAME)
    
    return subject, body

def create_email_message(to, subject, body, thread_id=None):
    """Create email message with optional thread ID for replies."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message['subject'] = subject
    
    msg = MIMEText(body)
    message.attach(msg)
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    email_data = {'raw': raw}
    
    if thread_id:
        email_data['threadId'] = thread_id
    
    return email_data

def send_email(service, message):
    """Send email using Gmail API."""
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        logging.info(f"Email sent successfully. Message ID: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        logging.error(f"Error sending email: {error.resp.status} - {error._get_reason()}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error sending email: {str(e)}")
        return None

def update_campaign_status(worksheet, email, status, email_number=None, thread_id=None):
    """Update campaign status in Google Sheets."""
    try:
        # Find the row with the email address
        cell = worksheet.find(email)
        row = cell.row
        
        # Update status
        worksheet.update_cell(row, 5, status)
        
        # Update sent date if applicable
        if email_number:
            date_column = email_number + 1  # Column B is 2, C is 3, D is 4
            worksheet.update_cell(row, date_column, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Store thread ID if provided
        if thread_id:
            worksheet.update_cell(row, 6, thread_id)  # Column F for Thread ID
            
    except Exception as e:
        logging.error(f"Error updating sheet for {email}: {str(e)}")

def process_campaign():
    """Main function to process the email campaign."""
    try:
        # Initialize services
        gmail_service = get_gmail_service()
        if not gmail_service:
            logging.error("Failed to initialize Gmail service")
            return
            
        sheets_client = get_sheets_client()
        if not sheets_client:
            logging.error("Failed to initialize Sheets client")
            return
        
        # Open spreadsheet and worksheet
        spreadsheet = sheets_client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Get all records
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        if df.empty:
            logging.info("No records found in the spreadsheet")
            return
            
        logging.info(f"Processing {len(df)} records")
        
        # Process each record
        for index, row in df.iterrows():
            email = row['Email Address']
            status = row['Status']
            thread_id = row.get('Thread ID', '')
            
            if status == 'Reply Received':
                continue
                
            current_date = datetime.now()
            
            # First email
            if status == 'Pending':
                subject, body = load_email_template('email_1.txt')
                message = create_email_message(email, subject, body)
                sent = send_email(gmail_service, message)
                
                if sent:
                    update_campaign_status(worksheet, email, 'Sent Email 1', 1, sent.get('threadId'))
                    logging.info(f"Sent first email to {email}")
                    logging.info(f"Waiting {EMAIL_SEND_DELAY} minutes before sending next email...")
                    time.sleep(EMAIL_SEND_DELAY * 60)  # Convert minutes to seconds
            
            # Second email
            elif status == 'Sent Email 1':
                email1_date = datetime.strptime(row['Date of Email 1 Sent'], '%Y-%m-%d %H:%M:%S')
                if current_date - email1_date >= timedelta(days=FOLLOWUP_1_DELAY):
                    subject, body = load_email_template('email_2.txt')
                    message = create_email_message(email, subject, body, thread_id)
                    sent = send_email(gmail_service, message)
                    
                    if sent:
                        update_campaign_status(worksheet, email, 'Sent Email 2', 2)
                        logging.info(f"Sent second email to {email}")
                        logging.info(f"Waiting {EMAIL_SEND_DELAY} minutes before sending next email...")
                        time.sleep(EMAIL_SEND_DELAY * 60)  # Convert minutes to seconds
            
            # Third email
            elif status == 'Sent Email 2':
                email2_date = datetime.strptime(row['Date of Email 2 Sent'], '%Y-%m-%d %H:%M:%S')
                if current_date - email2_date >= timedelta(days=FOLLOWUP_2_DELAY):
                    subject, body = load_email_template('email_3.txt')
                    message = create_email_message(email, subject, body, thread_id)
                    sent = send_email(gmail_service, message)
                    
                    if sent:
                        update_campaign_status(worksheet, email, 'Sent Email 3', 3)
                        logging.info(f"Sent third email to {email}")
                        logging.info(f"Waiting {EMAIL_SEND_DELAY} minutes before sending next email...")
                        time.sleep(EMAIL_SEND_DELAY * 60)  # Convert minutes to seconds
    
    except Exception as e:
        logging.error(f"Campaign processing error: {str(e)}")
        raise  # Re-raise the exception for debugging

if __name__ == "__main__":
    process_campaign() 