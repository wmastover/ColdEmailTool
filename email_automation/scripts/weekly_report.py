import pandas as pd
import gspread
from google.oauth2 import service_account
from dotenv import load_dotenv
from ..config.config import *
from ..utils.telegram_notifier import send_telegram_message

# Load environment variables
load_dotenv()

def get_sheets_client():
    """Initialize and return Google Sheets client."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SHEETS_SCOPES
    )
    return gspread.authorize(credentials)

def generate_report():
    """Generate a weekly status report and send it via Telegram."""
    try:
        # Initialize Sheets client
        sheets_client = get_sheets_client()
        
        # Open spreadsheet and get campaign data
        spreadsheet = sheets_client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # Calculate metrics
        total_contacts = len(df)
        total_replies = df[df['Status'] == 'Reply Received'].shape[0]
        conversion_rate = (total_replies / total_contacts) * 100 if total_contacts > 0 else 0
        
        # Create report message
        report_message = (
            f"📊 <b>Weekly Status Report</b>\n\n"
            f"Total Contacts: {total_contacts}\n"
            f"Total Replies: {total_replies}\n"
            f"Conversion Rate: {conversion_rate:.2f}%\n"
        )
        
        # Send report via Telegram
        send_telegram_message(report_message)
        print("✅ Weekly report sent successfully!")
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        print(error_msg)
        send_telegram_message(f"⚠️ <b>Error in Weekly Report Generation</b>\n\n{error_msg}")

if __name__ == "__main__":
    generate_report() 