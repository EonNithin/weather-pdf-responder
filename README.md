# Weather-Enhanced PDF Responder via Gmail

An automated Python system that processes Gmail inbox emails, adds weather information to PDF attachments, and sends replies with updated documents.

## Overview

This application:
1. Logs into a Gmail inbox using IMAP/SMTP
2. Searches for unread emails with subject "Local-weather-update"
3. Validates sender authorization against an Excel whitelist
4. Downloads PDF attachments from eligible emails
5. Appends current weather data to each page of each PDF
6. Replies to sender with updated PDFs attached

## Features

✅ **Gmail Integration**: IMAP/SMTP authentication and email processing  
✅ **Email Authorization**: Excel-based sender validation  
✅ **PDF Processing**: Weather data overlay on all pages  
✅ **Weather API**: OpenWeatherMap integration  
✅ **Automated Response**: Reply with updated PDFs  
✅ **Logging**: JSON-based activity logging  

### Bonus Features Implemented

- ✅ Processing logs in JSON format
- ✅ Modular code structure with comprehensive error handling
- ✅ Configurable weather city (default: New York)

## Tech Stack

- **Email**: `imaplib`, `smtplib`, `email`
- **Excel**: `pandas`, `openpyxl`
- **PDF**: `PyPDF2`, `reportlab`
- **Weather API**: `requests` with OpenWeatherMap
- **Environment**: `python-dotenv`

## Setup Instructions

### 1. Prerequisites

- Python 3.7+
- Gmail account with App Password enabled
- OpenWeatherMap API key

### 2. Gmail Configuration

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail" application
   - Save this 16-character password

### 3. OpenWeatherMap API Key

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key from the dashboard

### 4. Installation

```bash
# Clone or download the project
cd weather-pdf-responder

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

### 5. Environment Configuration

Edit `.env` file:

```env
# Gmail Configuration
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Weather API Configuration  
WEATHER_API_KEY=your_openweathermap_api_key

# Optional: Email processing settings
PROCESSED_LABEL=ProcessedWeatherRequests
```

### 6. Authorized Senders

Edit `allowed_senders.xlsx` to add authorized email addresses:

| email | name |
|-------|------|
| john.doe@example.com | John Doe |
| jane.smith@company.com | Jane Smith |

## Usage

### Run the Application

```bash
python main.py
```

### How It Works

1. **Email Processing**: Script searches for unread emails with subject "Local-weather-update"
2. **Authorization Check**: Validates sender against `allowed_senders.xlsx`
3. **PDF Processing**: Downloads PDF attachments and adds weather overlay
4. **Weather Data**: Fetches current weather for configured city (default: New York)
5. **Response**: Sends reply with updated PDFs attached

### Sample Email Flow

**Input Email:**
- Subject: `Local-weather-update`
- From: authorized sender
- Attachments: PDF files

**Output Response:**
- Subject: `Re: Local-weather-update`
- Body: Confirmation message
- Attachments: PDFs with weather data appended

## Project Structure

```
weather-pdf-responder/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your environment (create this)
├── allowed_senders.xlsx   # Authorized senders list
├── README.md              # This file
└── processing_log.json    # Generated activity log
```

## Weather Data Format

The weather information appended to PDFs includes:

- **City**: Weather location
- **Description**: Weather condition
- **Temperature**: Current temperature in Celsius
- **Humidity**: Humidity percentage
- **Wind Speed**: Wind speed in m/s
- **Timestamp**: When the data was fetched

## Logging

Activity logs are saved to `processing_log.json` with:
- Timestamp of each activity
- Processing messages
- Sender information
- Error details

## Error Handling

The application handles:
- Gmail authentication failures
- Missing or invalid weather API keys
- PDF processing errors
- Network connectivity issues
- Unauthorized sender attempts

## Security Notes

- Use Gmail App Passwords (not regular password)
- Store credentials in `.env` file (never commit to git)
- Validate all senders against whitelist
- Process only specific subject line emails

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify Gmail App Password is correct
   - Ensure 2FA is enabled on Gmail account

2. **Weather API Errors**
   - Check OpenWeatherMap API key validity
   - Verify API quota not exceeded

3. **PDF Processing Fails**
   - Ensure PDF attachments are not corrupted
   - Check PDF file permissions

4. **No Emails Found**
   - Verify subject line matches exactly: "Local-weather-update"
   - Check emails are unread
   - Confirm sender is in allowed_senders.xlsx

### Debug Mode

Add debug logging by modifying the log level in `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

This project is for educational/demonstration purposes.

---

**Note**: This system processes emails automatically. Test thoroughly in a development environment before using with production Gmail accounts.
