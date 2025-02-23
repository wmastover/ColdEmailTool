import gspread
from google.oauth2 import service_account

# Initialize the Sheets client
credentials = service_account.Credentials.from_service_account_file(
    'email_automation/config/credentials.json',
    scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
)

gc = gspread.authorize(credentials)
sheet = gc.open('Email Outreach Backend').worksheet('Sheet1')

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