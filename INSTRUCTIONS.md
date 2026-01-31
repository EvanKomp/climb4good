# Climb for Charity: Registration & Prize Pool App

## Project Overview

Build a Streamlit web application for a charity climbing event called "Community Sends: Climb for Charity." The app serves two purposes:

1. **Registration Form**: Collect participant signups with intended donation amounts
2. **Prize Pool Display**: Show real-time total of intended donations

All data flows through a Google Sheet—the app writes registrations to the sheet and reads from it to display the prize pool total.

## Tech Stack

- **Frontend/Backend**: Streamlit (Python)
- **Database**: Google Sheets (via Google Sheets API)
- **Authentication**: Google Service Account (for Sheets API access)
- **Hosting**: Streamlit Community Cloud (free tier)
- **Repository**: GitHub

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit App                         │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │  Registration Form  │  │   Prize Pool Display     │  │
│  │  - Name/pseudonym   │  │   - Total amount         │  │
│  │  - Email            │  │   - Participant count    │  │
│  │  - Category (M/W)   │  │   - Recent registrations │  │
│  │  - Donation amount  │  │   - Auto-refresh         │  │
│  └──────────┬──────────┘  └─────────────▲────────────┘  │
│             │ WRITE                     │ READ          │
└─────────────┼───────────────────────────┼───────────────┘
              │                           │
              ▼                           │
        ┌─────────────────────────────────┴───┐
        │           Google Sheet              │
        │  Columns: Timestamp, Name, Email,   │
        │           Category, Amount          │
        └─────────────────────────────────────┘
```

## File Structure

```
climb-for-charity/
├── .streamlit/
│   └── secrets.toml          # Google credentials (local dev only, not committed)
├── src/
│   ├── __init__.py
│   ├── sheets.py             # Google Sheets read/write functions
│   └── config.py             # App configuration constants
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

## Google Sheets Setup Requirements

### Sheet Structure

Create a Google Sheet with the following columns in row 1:

| A | B | C | D | E |
|---|---|---|---|---|
| timestamp | name | email | category | amount |

- **timestamp**: ISO format datetime string (e.g., "2025-01-30T14:30:00")
- **name**: String, participant name or pseudonym
- **email**: String, valid email address
- **category**: String, either "Men" or "Women"
- **amount**: Number, intended donation amount in dollars (minimum 20)

### Google Cloud Setup

The app needs a Google Cloud service account to read/write to the sheet:

1. Create a Google Cloud project at console.cloud.google.com
2. Enable the Google Sheets API
3. Create a Service Account (IAM & Admin → Service Accounts)
4. Create and download a JSON key for the service account
5. Share the Google Sheet with the service account email (give Editor access)

The service account email looks like: `your-service-account@your-project.iam.gserviceaccount.com`

## Detailed Component Requirements

### 1. Configuration (src/config.py)

```python
# Constants that should be defined:

APP_TITLE = "Community Sends: Climb for Charity"
EVENT_DATE = "TBD"  # Update when known
EVENT_LOCATION = "Shelf Road - The Banks"

MINIMUM_DONATION = 20
DEFAULT_DONATION = 20

VENMO_HANDLE = "@YourVenmoHandle"  # UPDATE THIS

CATEGORY_OPTIONS = ["Men", "Women"]

# Google Sheets config
SPREADSHEET_ID = "your-spreadsheet-id-here"  # From sheet URL
WORKSHEET_NAME = "Sheet1"  # Or whatever the tab is named
```

### 2. Google Sheets Integration (src/sheets.py)

Implement the following functions using the `gspread` library:

#### `get_sheets_client()`
- Authenticate using service account credentials from Streamlit secrets
- Return an authorized gspread client
- Handle authentication errors gracefully

#### `append_registration(name: str, email: str, category: str, amount: float) -> bool`
- Append a new row to the sheet with current timestamp
- Return True on success, False on failure
- Include error handling and logging

#### `get_all_registrations() -> pd.DataFrame`
- Fetch all rows from the sheet
- Return as a pandas DataFrame
- Handle empty sheet case (return empty DataFrame with correct columns)
- Cache results briefly (30-60 seconds) to avoid API rate limits

#### `get_prize_pool_stats() -> dict`
- Calculate and return:
  - `total_amount`: Sum of all donation amounts
  - `participant_count`: Number of registrations
  - `men_count`: Number in Men category
  - `women_count`: Number in Women category
- Use caching to minimize API calls

### 3. Main Application (app.py)

#### Page Configuration
- Set page title, icon (use 🧗 or 🏔️), and layout (wide or centered)
- Add custom CSS for styling (see Styling section below)

#### Layout Structure

The app should have two main sections, either as:
- **Option A**: Tabs ("Register" and "Prize Pool")
- **Option B**: Sidebar for registration, main area for prize pool display
- **Option C**: Single scrolling page with both sections

Recommend **Option A (tabs)** for cleaner UX.

#### Registration Form Tab/Section

Include the following form fields:

1. **Name/Pseudonym** (text input)
   - Required field
   - Placeholder: "Enter your name or a fun pseudonym"
   - Validation: non-empty, reasonable length (2-50 chars)

2. **Email** (text input)
   - Required field
   - Placeholder: "your@email.com"
   - Validation: basic email format check
   - Note: This is for confirmation/updates only

3. **Category** (selectbox or radio buttons)
   - Options: "Men", "Women"
   - Include helper text: "Non-binary participants can choose which group to compete in"

4. **Intended Donation Amount** (number input)
   - Minimum: $20
   - Default: $20
   - Step: $5 or $1
   - **Label**: "How much do you plan to donate?" or "Pledge Amount"
   - Include helper text: "This is for prize pool tracking only — you'll pay separately via Venmo or cash at the event. Minimum $20, more is always welcome!"

5. **Submit Button**
   - Text: "Register for Climb for Charity"
   - On click: validate inputs, write to sheet, show success message

#### Post-Registration Success Display

After successful registration, show:

1. **Confirmation message**: "You're registered! 🎉"

2. **Payment instructions box** (use st.info or styled container):
   ```
   💰 Now complete your donation!
   
   You pledged: ${amount}
   
   Pay via Venmo: @YourVenmoHandle
   (Include your name in the Venmo note)
   
   — OR —
   
   Bring cash to the event and pay at check-in.
   
   Your pledge is counting toward our prize pool total!
   ```

3. **Event details reminder**:
   - Date, location, schedule highlights

4. **Option to register another person** (button to reset form)

#### Prize Pool Display Tab/Section

This should be visually impactful and auto-refresh. Note: This displays **pledged** amounts, not verified payments.

1. **Large Prize Pool Total**
   - Big, bold number with dollar sign
   - Label as "Pledged Prize Pool" or "Projected Prize Pool"
   - Animated counter effect if possible (nice to have)
   - Example: Display "$1,420" in large font

2. **Participant Stats**
   - Total registered: X climbers
   - Men's category: X
   - Women's category: X

3. **Recent Registrations Feed** (optional but nice)
   - Show last 5-10 registrations
   - Display: Name and category only (not email or amount for privacy)
   - Format: "🧗 Alex joined Team Women!"

4. **Auto-Refresh**
   - Use `st.rerun()` with a timer or st.empty() pattern
   - Refresh every 30-60 seconds
   - Show "Last updated: X seconds ago" indicator

### 4. Styling Requirements

#### Color Scheme Suggestions (customize as desired)
- Primary: Earthy tones (browns, greens) for climbing theme
- Accent: Bright orange or yellow for CTAs
- Background: Light/clean

#### Custom CSS to Include

```css
/* Large prize pool display */
.prize-pool-total {
    font-size: 4rem;
    font-weight: bold;
    text-align: center;
    color: #2E7D32;  /* Green */
}

/* Stats cards */
.stat-card {
    background: #f5f5f5;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

/* Registration success box */
.success-box {
    background: #E8F5E9;
    border-left: 4px solid #4CAF50;
    padding: 1rem;
    border-radius: 4px;
}
```

Use `st.markdown()` with `unsafe_allow_html=True` for custom styled elements.

#### Mobile Responsiveness
- Streamlit handles most of this automatically
- Test that form inputs are usable on mobile
- Ensure prize pool numbers are readable on small screens

### 5. Error Handling

Implement graceful error handling for:

1. **Google Sheets API errors**
   - Connection failures: Show friendly message, allow retry
   - Rate limiting: Implement exponential backoff
   - Authentication errors: Log details, show generic error to user

2. **Form validation errors**
   - Show inline error messages
   - Don't clear form on validation failure

3. **Network issues**
   - Handle timeouts gracefully
   - Show cached data if available with "offline" indicator

### 6. Caching Strategy

Use Streamlit's caching decorators:

```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_prize_pool_stats():
    ...

@st.cache_resource  # Cache the client connection
def get_sheets_client():
    ...
```

## Dependencies (requirements.txt)

```
streamlit>=1.28.0
gspread>=5.12.0
google-auth>=2.23.0
pandas>=2.0.0
```

## Secrets Configuration

### What to Do With Your Google JSON Key File

When you create a service account and download the JSON key, you'll get a file like `your-project-abc123.json`. Here's what to do with it:

**DO NOT commit this file to GitHub** — it contains private credentials.

**For Local Development:**
1. Create a folder called `.streamlit` in your project root
2. Create a file called `secrets.toml` inside it
3. Open your JSON key file and copy its contents into `secrets.toml` in the format shown below
4. Add `.streamlit/secrets.toml` to your `.gitignore`

**For Production (Streamlit Cloud):**
1. Go to your app's dashboard on share.streamlit.io
2. Click "Settings" → "Secrets"
3. Paste the same TOML-formatted secrets there
4. Streamlit Cloud stores these encrypted, never in your repo

**Converting JSON to TOML format:**

Your downloaded JSON looks like this:
```json
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key": "-----BEGIN PRIVATE KEY-----\nABC123...\n-----END PRIVATE KEY-----\n",
  "client_email": "my-account@my-project.iam.gserviceaccount.com",
  ...
}
```

Convert it to TOML format for Streamlit secrets:
```toml
[gcp_service_account]
type = "service_account"
project_id = "my-project"
private_key = "-----BEGIN PRIVATE KEY-----\nABC123...\n-----END PRIVATE KEY-----\n"
client_email = "my-account@my-project.iam.gserviceaccount.com"
# ... copy all other fields from the JSON
```

The key insight: each JSON key becomes a line under `[gcp_service_account]`, with values in quotes.

### Local Development (.streamlit/secrets.toml)

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

[sheets]
spreadsheet_id = "your-spreadsheet-id-from-url"
worksheet_name = "Sheet1"

[app]
venmo_handle = "@YourVenmoHandle"
```

### Production (Streamlit Cloud)

Add these same secrets in the Streamlit Cloud dashboard under app settings.

## Deployment Steps

1. **Create GitHub repository**
   - Initialize repo with the file structure above
   - Add `.gitignore` to exclude `.streamlit/secrets.toml`

2. **Push code to GitHub**

3. **Deploy on Streamlit Community Cloud**
   - Go to share.streamlit.io
   - Connect your GitHub account
   - Select the repository and branch
   - Set `app.py` as the main file
   - Add secrets in the dashboard (copy from secrets.toml)
   - Deploy

4. **Test the deployed app**
   - Submit a test registration
   - Verify it appears in Google Sheet
   - Verify prize pool updates

## Testing Checklist

- [ ] Form validates required fields
- [ ] Form rejects donations under $20
- [ ] Successful submission writes to Google Sheet
- [ ] Success message displays with correct amount and Venmo handle
- [ ] Prize pool total calculates correctly
- [ ] Prize pool refreshes automatically
- [ ] App works on mobile devices
- [ ] App handles Google Sheets API errors gracefully
- [ ] Secrets are not exposed in code or logs

## Future Enhancements (Out of Scope for Now)

- Email confirmation via SendGrid/Mailgun
- QR code generation for Venmo payment
- Admin panel to mark payments as received
- Leaderboard preview by category
- Countdown timer to event
- Photo upload for Style Sender category

## Questions to Clarify with User

1. Confirm Venmo handle to display
2. Any specific color scheme or branding?
3. Want to show individual registration names publicly, or keep anonymous?
4. Any goal amount to show progress toward?
5. Need a "wall of fame" showing all registered participants?