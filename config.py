"""
Configuration settings for 13F Comparison App.
Centralized configuration following best practices.
"""

# SEC API Configuration
SEC_API_BASE_URL = "https://data.sec.gov"
SEC_ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"

# User-Agent is required by SEC
# Format: "CompanyName ContactEmail"
SEC_USER_AGENT = "Uber Investment Research research@uber.com"

# Rate Limiting (SEC allows 10 requests/second)
SEC_RATE_LIMIT_REQUESTS = 10
SEC_RATE_LIMIT_PERIOD = 1.0  # seconds

# Request Timeouts
REQUEST_TIMEOUT = 30  # seconds

import os

# Application Settings
DEBUG = True  # Set to False in production
HOST = "0.0.0.0"  # Allow external connections
PORT = 5000

# Development Settings
# Check for 'DEV' environment variable
# Run with: DEV=1 python app.py
DISABLE_AUTH_IN_DEV = os.environ.get('DEV') == '1'

# Flask Settings
#Flask Settings
SECRET_KEY = "dev-random-string-change-in-prod-xyz-123" # Used for session encryption

# Authentication
# Password hash for login verification 
# Original password known only to authorized users
# Using pbkdf2:sha256 for compatibility
PASSWORD_HASH = "pbkdf2:sha256:1000000$6fby0KFOwjtF5uTJ$22645a4f24ca69c3fcc4badfbfb60c60009ff4b7fbe5d1c2bcecadae71553d2c"

# Data Display Settings
MAX_DISPLAY_ROWS = 1000  # Maximum rows to show in results
DEFAULT_SORT_BY = "current_value"  # Default sort column
DEFAULT_SORT_ORDER = "desc"  # 'asc' or 'desc'

# Example CIKs for user reference
EXAMPLE_CIKS = {
    "RA Capital Management": "0001346824",
    "Perceptive Advisors": "Find at sec.gov",
    "OrbiMed Advisors": "Find at sec.gov",
}

