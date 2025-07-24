import os
import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import decode_header
import pandas as pd
import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from io import BytesIO
import tempfile
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherPDFResponder:
    def __init__(self):
        self.gmail_user = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.processed_label = os.getenv('PROCESSED_LABEL', 'ProcessedWeatherRequests')
        self.subject_filter = "Local-weather-update"
        self.default_city = input("Enter your city: ")  #City for weather 
        self.processing_log = []
        
    def log_activity(self, message, email_from=None):
        """Log processing activities"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "sender": email_from
        }
        self.processing_log.append(log_entry)
        print(f"[{log_entry['timestamp']}] {message}")
        
    def load_allowed_senders(self):
        """Load authorized sender emails from Excel file"""
        try:
            df = pd.read_excel('allowed_senders.xlsx')
            allowed_emails = df['email'].str.lower().tolist()
            self.log_activity(f"Loaded {len(allowed_emails)} allowed senders")
            return allowed_emails
        except Exception as e:
            self.log_activity(f"Error loading allowed senders: {str(e)}")
            return []
            
    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user, self.gmail_password)
            self.log_activity("Successfully connected to Gmail")
            return mail
        except Exception as e:
            self.log_activity(f"Failed to connect to Gmail: {str(e)}")
            return None
            
    def get_weather_data(self, city=None):
        """Fetch weather data from OpenWeatherMap API"""
        if not city:
            city = self.default_city
            
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.weather_api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                weather_info = {
                    'city': data['name'],
                    'description': data['weather'][0]['description'].title(),
                    'temperature': f"{data['main']['temp']}°C",
                    'humidity': f"{data['main']['humidity']}%",
                    'wind_speed': f"{data['wind']['speed']} m/s",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.log_activity(f"Weather data fetched for {city}")
                return weather_info
            else:
                self.log_activity(f"Weather API error: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            self.log_activity(f"Error fetching weather data: {str(e)}")
            return None
            
    def add_weather_to_pdf(self, pdf_content, weather_data):
        """Add weather information to PDF"""
        try:
            # Read the original PDF
            pdf_reader = PdfReader(BytesIO(pdf_content))
            pdf_writer = PdfWriter()
            
            # Create weather text
            weather_text = (
                f"Weather Update - {weather_data['timestamp']}\n"
                f"City: {weather_data['city']}\n"
                f"Description: {weather_data['description']}\n"
                f"Temperature: {weather_data['temperature']}\n"
                f"Humidity: {weather_data['humidity']}\n"
                f"Wind Speed: {weather_data['wind_speed']}"
            )
            
            # Process each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # Create a new PDF with weather info
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                
                # Add weather info to bottom of page
                can.setFont("Helvetica", 8)
                can.setFillColor(black)
                y_position = 50
                for line in weather_text.split('\n'):
                    can.drawString(50, y_position, line)
                    y_position -= 12
                    
                can.save()
                packet.seek(0)
                
                # Merge with original page
                overlay_pdf = PdfReader(packet)
                page.merge_page(overlay_pdf.pages[0])
                pdf_writer.add_page(page)
                
            # Return the modified PDF
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            self.log_activity("Weather data added to PDF")
            return output_buffer.getvalue()
            
        except Exception as e:
            self.log_activity(f"Error processing PDF: {str(e)}")
            return None
            
    def send_reply_email(self, original_email, updated_pdfs, recipient_email):
        """Send reply email with updated PDFs"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = recipient_email
            msg['Subject'] = f"Re: {self.subject_filter}"
            
            # Email body
            body = (
                "Hello,\n\n"
                "Thank you for your request. Please find attached the PDF(s) "
                "with current weather information appended to each page.\n\n"
                "Best regards,\n"
                "Automated Weather PDF Responder"
            )
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach updated PDFs
            for i, pdf_content in enumerate(updated_pdfs):
                pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=f'weather_updated_document_{i+1}.pdf'
                )
                msg.attach(pdf_attachment)
                
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            self.log_activity(f"Reply sent to {recipient_email} with {len(updated_pdfs)} updated PDFs")
            return True
            
        except Exception as e:
            self.log_activity(f"Error sending reply email: {str(e)}")
            return False
            
    def process_emails(self):
        """Main processing function"""
        self.log_activity("Starting email processing...")
        
        # Load allowed senders
        allowed_senders = self.load_allowed_senders()
        if not allowed_senders:
            self.log_activity("No allowed senders found. Exiting.")
            return
            
        # Connect to Gmail
        mail = self.connect_to_gmail()
        if not mail:
            return
            
        try:
            # Select inbox
            mail.select('inbox')
            
            # Search for unread emails with specific subject
            search_criteria = f'(UNSEEN SUBJECT "{self.subject_filter}")'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                self.log_activity("No matching emails found")
                return
                
            email_ids = messages[0].split()
            self.log_activity(f"Found {len(email_ids)} unread emails with subject '{self.subject_filter}'")
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                        
                    # Parse email
                    email_message = email.message_from_bytes(msg_data[0][1])
                    sender_email = email_message['From'].lower()
                    
                    # Extract email address from "Name <email@domain.com>" format
                    if '<' in sender_email:
                        sender_email = sender_email.split('<')[1].replace('>', '').strip()
                    
                    self.log_activity(f"Processing email from: {sender_email}")
                    
                    # Check if sender is authorized
                    if sender_email not in allowed_senders:
                        self.log_activity(f"Sender {sender_email} not authorized. Skipping.", sender_email)
                        continue
                        
                    # Extract PDF attachments
                    pdf_attachments = []
                    for part in email_message.walk():
                        if part.get_content_disposition() == 'attachment':
                            filename = part.get_filename()
                            if filename and filename.lower().endswith('.pdf'):
                                pdf_content = part.get_payload(decode=True)
                                pdf_attachments.append(pdf_content)
                                
                    if not pdf_attachments:
                        self.log_activity(f"No PDF attachments found in email from {sender_email}")
                        continue
                        
                    self.log_activity(f"Found {len(pdf_attachments)} PDF attachments")
                    
                    # Get weather data
                    weather_data = self.get_weather_data()
                    if not weather_data:
                        self.log_activity("Could not fetch weather data. Skipping email.")
                        continue
                        
                    # Process PDFs
                    updated_pdfs = []
                    for pdf_content in pdf_attachments:
                        updated_pdf = self.add_weather_to_pdf(pdf_content, weather_data)
                        if updated_pdf:
                            updated_pdfs.append(updated_pdf)
                            
                    if not updated_pdfs:
                        self.log_activity("No PDFs were successfully processed")
                        continue
                        
                    # Send reply
                    if self.send_reply_email(email_message, updated_pdfs, sender_email):
                        # Mark email as read
                        mail.store(email_id, '+FLAGS', '\\Seen')
                        self.log_activity(f"Successfully processed email from {sender_email}")
                    else:
                        self.log_activity(f"Failed to send reply to {sender_email}")
                        
                except Exception as e:
                    self.log_activity(f"Error processing individual email: {str(e)}")
                    continue
                    
        except Exception as e:
            self.log_activity(f"Error during email processing: {str(e)}")
        finally:
            mail.close()
            mail.logout()
            
        # Save processing log
        with open('processing_log.json', 'w') as f:
            json.dump(self.processing_log, f, indent=2)
            
        self.log_activity("Email processing completed")
        
def main():
    responder = WeatherPDFResponder()
    responder.process_emails()

if __name__ == '__main__':
    main()
