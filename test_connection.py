import gspread
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account

# Define the scopes
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://spreadsheets.google.com/feeds',
]

try:
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        'email_automation/config/credentials.json',
        scopes=scopes
    )
    
    # Connect to Google Sheets
    gc = gspread.authorize(credentials)
    print("Successfully authenticated with Google Sheets API!")
    
    # Try to open the spreadsheet
    try:
        spreadsheet = gc.open('Email Outreach Backend')
        print(f"Successfully opened spreadsheet: {spreadsheet.title}")
        
        # Try to access the worksheet
        try:
            worksheet = spreadsheet.worksheet('Sheet1')
            print(f"Successfully accessed worksheet: {worksheet.title}")
            
            # Get and print the data
            data = worksheet.get_all_records()
            print("\nCurrent data in the sheet:")
            print(data)
            
        except gspread.exceptions.WorksheetNotFound:
            print("Error: Could not find worksheet 'Sheet1'")
            print("Available worksheets:", [ws.title for ws in spreadsheet.worksheets()])
            
    except gspread.exceptions.SpreadsheetNotFound:
        print("Error: Could not find spreadsheet 'Email Outreach Backend'")
        print("Make sure you have shared the spreadsheet with:", credentials.service_account_email)
        
except Exception as e:
    print(f"Error during setup: {str(e)}") 