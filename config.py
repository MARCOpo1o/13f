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

# Application Settings
DEBUG = True  # Set to False in production
HOST = "0.0.0.0"  # Allow external connections
PORT = 5000

# Flask Settings
SECRET_KEY = "phantomfriends-secret-key-2024"  # Used for session encryption

# Authentication
# Password hash for login verification (password is NOT stored in plaintext)
# Original password known only to authorized users
PASSWORD_HASH = "scrypt:32768:8:1$f3GtbqDsdwPe6gHI$90a8375a17263ea7eb5975f502ca275dcc8fb967a836079d05a5cf5bf854b835f84b71da384853135e0517446f81e9cb71e157a85ec6752b4228c3e6562105c1"

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

