import gspread
from google.oauth2 import service_account
from email_automation.config.config import *

# Initialize the Sheets client
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE,
    scopes=SHEETS_SCOPES
)

gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# Get current headers
headers = sheet.row_values(1)

# Add Thread ID column if it doesn't exist
if 'Thread ID' not in headers:
    next_col = len(headers) + 1
    sheet.update_cell(1, next_col, 'Thread ID')

# Clear any existing rows with the test email
cells = sheet.findall('wmastover@gmail.com')
for cell in cells:
    sheet.delete_row(cell.row)

# Add the test email with Pending status
sheet.append_row(['wmastover@gmail.com', '', '', '', 'Pending', '']) 