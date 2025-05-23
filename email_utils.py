#!/usr/bin/env python3
"""
Shared Email Utilities
Provides email functionality for both command-line and GUI versions of the media manager.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import json
import os
import re


class EmailConfig:
    """Email configuration container"""
    def __init__(self, sender_name, sender_email, receiver_email, password, smtp_server, smtp_port):
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def is_valid(self):
        """Check if all required email configuration is present and valid"""
        # Check if all required fields are present
        required_fields = [
            self.sender_email, self.receiver_email, self.password, self.smtp_server
        ]
        if not all(field for field in required_fields):
            return False
        
        # Validate email addresses using basic regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.sender_email):
            return False
        if not re.match(email_pattern, self.receiver_email):
            return False
        
        # Validate SMTP port
        try:
            port = int(self.smtp_port)
            if not (1 <= port <= 65535):
                return False
        except (ValueError, TypeError):
            return False
        
        # Check for placeholder values
        placeholder_values = [
            "SENDER_NAME_HERE", "SENDER_EMAIL_HERE", "RECEIVER_EMAIL_HERE", 
            "PASSWORD_HERE", "smtp.server.com"
        ]
        config_values = [
            self.sender_email, self.receiver_email, self.password, self.smtp_server
        ]
        if any(val in placeholder_values for val in config_values):
            return False
        
        return True


def load_email_config_from_file(config_file="media_manager_config.json"):
    """
    Load email configuration from GUI config file
    
    Args:
        config_file (str): Path to the JSON configuration file
    
    Returns:
        EmailConfig or None: Email configuration object or None if loading fails
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                email_config = config.get("email", {})
                
                return EmailConfig(
                    sender_name=email_config.get("sender_name", ""),
                    sender_email=email_config.get("sender_email", ""),
                    receiver_email=email_config.get("receiver_email", ""),
                    password=email_config.get("password", ""),
                    smtp_server=email_config.get("smtp_server", "smtp.gmail.com"),
                    smtp_port=email_config.get("smtp_port", 587)
                )
    except Exception as e:
        print(f"Error loading email config from file: {e}")
    
    return None


def create_email_config_hardcoded():
    """
    Create email configuration with hardcoded values (for command-line script)
    
    Returns:
        EmailConfig: Email configuration object with hardcoded values
    
    Note:
        Users MUST update these values before using. The default values are
        intentionally invalid to prevent accidental usage.
        
        To configure:
        1. Edit this function in email_utils.py
        2. Replace placeholder values with your actual email settings
        3. For Gmail: use app passwords, not your regular password
    """
    return EmailConfig(
        sender_name="SENDER_NAME_HERE",
        sender_email="SENDER_EMAIL_HERE",
        receiver_email="RECEIVER_EMAIL_HERE",
        password="PASSWORD_HERE",
        smtp_server="smtp.server.com",
        smtp_port=587
    )


def send_email(email_config, subject, body, log_function=None):
    """
    Send an email using the provided configuration
    
    Args:
        email_config (EmailConfig): Email configuration object
        subject (str): Email subject
        body (str): Email body content
        log_function (callable, optional): Function to call for logging messages
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not email_config or not email_config.is_valid():
        error_msg = "Email configuration is incomplete or invalid"
        if log_function:
            log_function(error_msg)
        else:
            print(error_msg)
        return False
    
    try:
        message = MIMEMultipart()
        message["From"] = formataddr((email_config.sender_name, email_config.sender_email))
        message["To"] = email_config.receiver_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(email_config.smtp_server, int(email_config.smtp_port))
        server.starttls()
        server.login(email_config.sender_email, email_config.password)
        server.sendmail(email_config.sender_email, email_config.receiver_email, message.as_string())
        server.quit()
        
        success_msg = "Email notification sent successfully"
        if log_function:
            log_function(success_msg)
        else:
            print(success_msg)
        return True
        
    except Exception as e:
        error_msg = f"Error sending email: {e}"
        if log_function:
            log_function(error_msg)
        else:
            print(error_msg)
        return False


def send_missing_media_email(missing_titles, email_config=None, config_file=None, log_function=None):
    """
    Send an email notification about missing media files
    
    Args:
        missing_titles (list or set): Collection of missing media titles
        email_config (EmailConfig, optional): Email configuration object
        config_file (str, optional): Path to config file (if email_config not provided)
        log_function (callable, optional): Function to call for logging messages
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Load email config if not provided
    if not email_config:
        if config_file:
            email_config = load_email_config_from_file(config_file)
        else:
            email_config = create_email_config_hardcoded()
    
    if not email_config or not email_config.is_valid():
        error_msg = "Cannot send email: email configuration is incomplete"
        if log_function:
            log_function(error_msg)
        else:
            print(error_msg)
        return False
    
    subject = "Missing Media Files Detected"
    body = f"The following {len(missing_titles)} media files are missing:\n\n" + '\n'.join(sorted(missing_titles))
    
    return send_email(email_config, subject, body, log_function)
