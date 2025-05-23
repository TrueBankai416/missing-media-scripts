#!/usr/bin/env python3
"""
Email Debug Test Script
Tests email sending with debug logging to troubleshoot sender name issues
"""

import json
import os
from email_utils import EmailConfig, send_email, load_email_config_from_file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

def load_config():
    """Load configuration from GUI config file"""
    return load_email_config_from_file("media_manager_config.json")

def test_email_method_1(email_config, test_body):
    """Test Method 1: Using shared email_utils module"""
    print("\n=== Testing Method 1: Shared email_utils module ===")
    
    try:
        subject = "Debug Test - Method 1 (email_utils module)"
        success = send_email(email_config, subject, test_body, print)
        
        if success:
            print("✓ Method 1 sent successfully")
            return True
        else:
            print("✗ Method 1 failed")
            return False
        
    except Exception as e:
        print(f"✗ Method 1 failed: {e}")
        return False

def test_email_method_2(email_config, test_body):
    """Test Method 2: Direct string format (like Vaultwarden)"""
    print("\n=== Testing Method 2: Direct string format ===")
    
    try:
        message = MIMEMultipart()
        from_header = f"{email_config.sender_name} <{email_config.sender_email}>"
        print(f"Setting From header to: {from_header}")
        
        message["From"] = from_header
        message["To"] = email_config.receiver_email
        message["Subject"] = "Debug Test - Method 2 (Direct String)"
        
        message.attach(MIMEText(test_body, "plain"))
        
        # Show all headers before sending
        print("Headers being sent:")
        for key, value in message.items():
            print(f"  {key}: {value}")
        
        # Send email
        server = smtplib.SMTP(email_config.smtp_server, int(email_config.smtp_port))
        server.starttls()
        server.login(email_config.sender_email, email_config.password)
        server.sendmail(email_config.sender_email, email_config.receiver_email, message.as_string())
        server.quit()
        
        print("✓ Method 2 sent successfully")
        return True
        
    except Exception as e:
        print(f"✗ Method 2 failed: {e}")
        return False

def test_email_method_3(email_config, test_body):
    """Test Method 3: Multiple headers approach"""
    print("\n=== Testing Method 3: Multiple headers ===")
    
    try:
        message = MIMEMultipart()
        from_header = formataddr((email_config.sender_name, email_config.sender_email))
        
        message["From"] = from_header
        message["Reply-To"] = from_header
        message["Sender"] = email_config.sender_email
        message["To"] = email_config.receiver_email
        message["Subject"] = "Debug Test - Method 3 (Multiple Headers)"
        
        print(f"Setting From header to: {from_header}")
        print(f"Setting Reply-To header to: {from_header}")
        print(f"Setting Sender header to: {email_config.sender_email}")
        
        message.attach(MIMEText(test_body, "plain"))
        
        # Show all headers before sending
        print("Headers being sent:")
        for key, value in message.items():
            print(f"  {key}: {value}")
        
        # Send email
        server = smtplib.SMTP(email_config.smtp_server, int(email_config.smtp_port))
        server.starttls()
        server.login(email_config.sender_email, email_config.password)
        server.sendmail(email_config.sender_email, email_config.receiver_email, message.as_string())
        server.quit()
        
        print("✓ Method 3 sent successfully")
        return True
        
    except Exception as e:
        print(f"✗ Method 3 failed: {e}")
        return False

def main():
    print("Email Debug Test Script")
    print("======================")
    
    # Load configuration
    email_config = load_config()
    if not email_config:
        print("Could not load configuration. Make sure media_manager_config.json exists.")
        return
    
    # Verify email config
    if not email_config.is_valid():
        print("Email configuration is incomplete. Please check your settings.")
        return
    
    print("Current email configuration:")
    print(f"  Sender Name: '{email_config.sender_name}'")
    print(f"  Sender Email: '{email_config.sender_email}'")
    print(f"  Receiver Email: '{email_config.receiver_email}'")
    print(f"  SMTP Server: {email_config.smtp_server}:{email_config.smtp_port}")
    
    test_body = f"""This is a debug test email sent at various times to test sender name display.

Current configuration:
- Sender Name: {email_config.sender_name}
- Sender Email: {email_config.sender_email}

Please check how the sender name appears in your email client and compare between the different test methods.
"""
    
    # Test all methods
    print(f"\nSending test emails to: {email_config.receiver_email}")
    print("You should receive 3 test emails with different methods...")
    
    test_email_method_1(email_config, test_body + "\nThis email was sent using Method 1 (formataddr)")
    test_email_method_2(email_config, test_body + "\nThis email was sent using Method 2 (Direct String)")
    test_email_method_3(email_config, test_body + "\nThis email was sent using Method 3 (Multiple Headers)")
    
    print("\n" + "="*50)
    print("Debug test complete!")
    print("Check your email inbox and compare how the sender name")
    print("appears for each of the 3 test emails.")
    print("Let me know which method (if any) shows the sender name correctly.")

if __name__ == "__main__":
    main()
