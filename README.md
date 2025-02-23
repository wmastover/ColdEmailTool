# Email Automation System

An automated email campaign system that uses Google Sheets as a backend and Gmail API for sending emails and tracking responses.

## Features

- Automated email campaign management using Google Sheets
- Three-stage email sequence with customizable templates
- Automatic reply detection and campaign status updates
- Configurable follow-up intervals
- Detailed logging of all operations

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- Gmail API enabled
- Google Sheets API enabled
- Service account credentials

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd email-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud Platform:
   - Create a new project in Google Cloud Console
   - Enable Gmail API and Google Sheets API
   - Create service account credentials
   - Download credentials as `credentials.json` and place in `config/` directory

4. Create a `.env` file in the root directory with the following variables:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Your Name
```

5. Set up Google Sheets:
   - Create a new Google Sheet named "Email Campaign Tracker"
   - Create a worksheet named "Campaign Data" with the following columns:
     - Email Address
     - Date of Email 1 Sent
     - Date of Email 2 Sent
     - Date of Email 3 Sent
     - Status

6. Customize email templates:
   - Edit the template files in the `templates/` directory:
     - `email_1.txt`: Initial email
     - `email_2.txt`: First follow-up
     - `email_3.txt`: Final follow-up

## Usage

1. Add target email addresses to the Google Sheet with status "Pending"

2. Run the email sending script:
```bash
python -m email_automation.scripts.send_emails
```

3. Run the reply detection script:
```bash
python -m email_automation.scripts.detect_replies
```

4. Set up cron jobs for automation:
```bash
# Example cron jobs
0 9 * * * cd /path/to/email-automation && python -m email_automation.scripts.send_emails
0 */4 * * * cd /path/to/email-automation && python -m email_automation.scripts.detect_replies
```

## Configuration

Edit `config/config.py` to modify:
- Follow-up intervals
- Spreadsheet and worksheet names
- Logging settings
- API scopes

## Logging

Logs are stored in the `logs/` directory:
- `email_log.txt`: Records all email sending operations
- `error_log.txt`: Records errors and reply detection operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 