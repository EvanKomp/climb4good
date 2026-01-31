"""Configuration constants for the Climb for Charity app."""

# App metadata
APP_TITLE = "Climb4Good"
EVENT_DATE = "April 10-12, 2026"
EVENT_LOCATION = "Shelf Road - The Banks"

# Donation settings
MINIMUM_DONATION = 20
DEFAULT_DONATION = 20

# Payment info
VENMO_HANDLE = "@Evan-Komp"

# Competition categories
CATEGORY_OPTIONS = ["Men", "Women"]

# Google Sheets configuration
# These will be overridden by st.secrets in production
SPREADSHEET_ID = "your-spreadsheet-id-here"  # From sheet URL
WORKSHEET_NAME = "Sheet1"  # Or whatever the tab is named

# Auto-refresh settings (seconds)
PRIZE_POOL_REFRESH_INTERVAL = 60

# Display settings
RECENT_REGISTRATIONS_COUNT = 10
