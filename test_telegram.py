from email_automation.utils.telegram_notifier import send_telegram_message
import html

def test_telegram():
    # Test basic message
    test_message = (
        f"🧪 <b>Test Message</b>\n\n"
        f"If you're seeing this message, your Telegram bot is configured correctly!\n"
        f"✅ Bot token is valid\n"
        f"✅ Chat ID is correct\n"
        f"✅ Message formatting works"
    )
    
    success = send_telegram_message(test_message)
    if success:
        print("✅ Basic test message sent successfully!")
    else:
        print("❌ Failed to send basic test message")

    # Test reply notification format with escaped characters
    message_id = "test123"
    sender = "John Doe <john@example.com>"
    subject = "Re: Saw your review - how does less returns sound?"
    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{html.escape(message_id)}"
    
    test_reply = (
        f"🔔 <b>New Reply Received!</b>\n\n"
        f"From: {html.escape(sender)}\n"
        f"Subject: {html.escape(subject)}\n"
        f"Status: Campaign status updated to 'Reply Received'\n\n"
        f"<a href='{gmail_link}'>View Email in Gmail</a>"
    )
    
    success = send_telegram_message(test_reply)
    if success:
        print("✅ Reply notification test message sent successfully!")
    else:
        print("❌ Failed to send reply notification test message")

if __name__ == "__main__":
    test_telegram() 