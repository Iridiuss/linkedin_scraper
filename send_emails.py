# import csv
# import smtplib
# import logging
# import time
# import os
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# logging.basicConfig(level=logging.INFO)

# # Get the directory where the script is located
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV_PATH = os.path.join(SCRIPT_DIR, "lead_plugins", "salesnav", "extracted_emails.csv")

# def read_emails_from_csv(filename=CSV_PATH):
#     email_list = []
#     try:
#         with open(filename, mode='r', encoding='utf-8') as file:
#             reader = csv.reader(file)
#             next(reader)  # Skip header row
#             for row in reader:
#                 if row:  # Check if row is not empty
#                     email_list.append(row[0])
#         return email_list
#     except Exception as e:
#         logging.error(f"Error reading CSV file: {str(e)}")
#         return []

# def send_emails(email_list):
#     # SMTP Configuration
#     SMTP_HOST = "smtp.hostinger.com"
#     SMTP_PORT = 465
#     SMTP_USER = "testsmtp@sumerudigital.com"
#     SMTP_PASS = "Smtp##8899"
    
#     # Create message
#     msg = MIMEMultipart()
#     msg['From'] = SMTP_USER
#     msg['Subject'] = "Innovative Tech Solutions for Your Next Big Idea"
    
#     # Email body
#     body = "hello this is testing"
#     msg.attach(MIMEText(body, 'plain'))
    
#     # Send emails
#     try:
#         # Connect to Hostinger SMTP server using SSL
#         server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
#         server.login(SMTP_USER, SMTP_PASS)
        
#         for email in email_list:
#             msg['To'] = email
#             server.send_message(msg)
#             logging.info(f"Email sent to: {email}")
#             time.sleep(1)  # Small delay between emails
            
#         server.quit()
#         logging.info("All emails sent successfully!")
#     except smtplib.SMTPAuthenticationError:
#         logging.error("Authentication failed. Please check your Hostinger email credentials.")
#     except Exception as e:
#         logging.error(f"Error sending emails: {str(e)}")

# def main():
#     logging.info("Starting email sending process...")
#     logging.info(f"Looking for CSV file at: {CSV_PATH}")
#     email_list = read_emails_from_csv()
    
#     if not email_list:
#         logging.error("No emails found in the CSV file or error reading the file")
#         return
    
#     logging.info(f"Found {len(email_list)} emails to send")
#     send_emails(email_list)

# if __name__ == "__main__":
#     main() 
import csv
import smtplib
import logging
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "lead_plugins", "salesnav", "extracted_data.csv")

def read_emails_from_csv(filename=CSV_PATH):
    data_list = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if row:  # Check if row is not empty
                    first_name = row[0]
                    last_name = row[1]
                    email = row[2]
                    data_list.append((first_name, last_name, email))
        return data_list
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return []

def send_emails(data_list):
    # Gmail SMTP Configuration
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 465  # SSL Port
    SMTP_USER = os.getenv("EMAIL_ID")  # Your Gmail email address
    SMTP_PASS = os.getenv("EMAIL_PASSWORD")  # Your Gmail password (or app password if 2FA enabled)
    
    # Email body template
    body_template = """Hi {first_name} {last_name},

At Sumeru Digital, we specialize in delivering innovative digital solutions for businesses, NGOs, and institutions worldwide. Whether you're scaling up or transforming digitally, we’re here to support with:

- Web & Mobile App Development – React, Flutter, .NET
- AI, Blockchain, NFTs & Smart Contracts
- Metaverse / XR Development – Unity, Blender, Unreal
- SEO, Digital Marketing & Event Tech Solutions

If you're planning a new platform, immersive experience, or tech-driven initiative—or know someone who is—we’d love to collaborate.

Feel free to reply here or refer us directly. Let’s create something exceptional together.
"""

    # Send emails
    try:
        # Connect to Gmail SMTP server using SSL
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        
        for first_name, last_name, email in data_list:
            # Create a new message for each recipient
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = email  # Set the "To" field
            msg['Subject'] = "Innovative Tech Solutions for Your Next Big Idea"
            
            # Format the body with dynamic first name, last name
            body = body_template.format(first_name=first_name, last_name=last_name)
            
            msg.attach(MIMEText(body, 'plain'))
            server.send_message(msg)
            logging.info(f"Email sent to: {email}")
            time.sleep(1)  # Small delay between emails
            
        server.quit()
        logging.info("All emails sent successfully!")
    except smtplib.SMTPAuthenticationError:
        logging.error("Authentication failed. Please check your Gmail email credentials.")
    except Exception as e:
        logging.error(f"Error sending emails: {str(e)}")

def main():
    logging.info("Starting email sending process...")
    logging.info(f"Looking for CSV file at: {CSV_PATH}")
    data_list = read_emails_from_csv()
    
    if not data_list:
        logging.error("No emails found in the CSV file or error reading the file")
        return
    
    logging.info(f"Found {len(data_list)} emails to send")
    send_emails(data_list)

if __name__ == "__main__":
    main()

