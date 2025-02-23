# Email Automation System

An automated email campaign system that uses Google Sheets as a backend and Gmail API for sending emails and tracking responses. Features Telegram notifications for real-time reply alerts and weekly status reports.

## Features

- Automated email campaign management using Google Sheets
- Three-stage email sequence with customizable templates
- Automatic reply detection with real-time Telegram notifications
- Weekly status reports via Telegram
- Direct Gmail links in notifications for quick access to replies
- Campaign status tracking and updates
- Detailed logging of all operations

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with:
  - Gmail API enabled
  - Google Sheets API enabled
  - Service account credentials
- Telegram account and bot (for notifications)

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
   - Download credentials as `credentials.json` and place in `email_automation/config/` directory

4. Set up Telegram Bot:
   - Create a new bot using BotFather in Telegram
   - Save the bot token
   - Send a message to your bot
   - Get your chat ID from the bot API

5. Create a `.env` file in the root directory with the following variables:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Your Name

# Google Sheets configuration
SPREADSHEET_NAME=Email Outreach Backend
WORKSHEET_NAME=Sheet1

# Email follow-up intervals (in days)
FOLLOWUP_1_DELAY=2
FOLLOWUP_2_DELAY=3

# Delay between sending emails (in minutes)
EMAIL_SEND_DELAY=2

# Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

6. Set up Google Sheets:
   - Create a new Google Sheet named "Email Outreach Backend"
   - Create a worksheet named "Sheet1" with the following columns:
     - Email Address
     - Date of Email 1 Sent
     - Date of Email 2 Sent
     - Date of Email 3 Sent
     - Status
     - Thread ID

7. Customize email templates:
   - Edit the template files in the `email_automation/templates/` directory:
     - `email_1.txt`: Initial email
     - `email_2.txt`: First follow-up
     - `email_3.txt`: Final follow-up

8. Schedule Weekly Status Reports:
   - Set up a cron job to run the weekly report script every Friday at 5 PM:
   ```bash
   0 17 * * 5 cd /path/to/email-automation && python -m email_automation.scripts.weekly_report
   ```

## Usage

1. Add test email to campaign:
```bash
python add_test_email.py
```

2. Send campaign emails:
```bash
python -m email_automation.scripts.send_emails
```

3. Check for replies:
```bash
python -m email_automation.scripts.detect_replies
```

4. Test Telegram notifications:
```bash
python test_telegram.py
```

## Automated Reply Detection

Set up cron jobs for automated reply checking:
```bash
# Example cron jobs
0 9 * * * cd /path/to/email-automation && python -m email_automation.scripts.send_emails
*/15 * * * * cd /path/to/email-automation && python -m email_automation.scripts.detect_replies
```

This will:
- Send scheduled emails daily at 9 AM
- Check for replies every 15 minutes
- Send Telegram notifications when replies are received

## Telegram Notifications

When a reply is received, you'll get a Telegram notification containing:
- Sender's name and email
- Email subject
- Campaign status update
- Direct link to view the email in Gmail

## Weekly Status Reports

Every Friday, you'll receive a Telegram message with:
- Total number of contacts
- Total number of replies
- Conversion rate (replies/contacts)

## Project Structure

```
email_automation/
├── config/
│   ├── config.py
│   └── serviceAccount.json
├── scripts/
│   ├── send_emails.py
│   ├── detect_replies.py
│   └── weekly_report.py
├── templates/
│   ├── email_1.txt
│   ├── email_2.txt
│   └── email_3.txt
├── utils/
│   └── telegram_notifier.py
└── logs/
    ├── email_log.txt
    └── error_log.txt
```

## Security

- Service account credentials and environment variables are never committed to Git
- All sensitive files are included in .gitignore
- Telegram notifications use HTML escaping to prevent injection
- API scopes are limited to necessary permissions only

## Troubleshooting

1. Check the log files in `email_automation/logs/` for detailed error messages
2. Ensure all credentials are properly set up and have correct permissions
3. Verify Telegram bot is active and has correct permissions
4. Test connection to Google services using `test_connection.py`
5. Test Telegram notifications using `test_telegram.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details 