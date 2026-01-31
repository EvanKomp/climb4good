# Climb4Good

A Streamlit web application for managing registration and prize pool tracking for a charity climbing event.

## 🏔️ Features

- **Registration Form**: Collect participant information and donation pledges
- **Live Prize Pool Display**: Real-time total of pledged donations with auto-refresh
- **Google Sheets Integration**: All data stored in Google Sheets (no database needed)
- **Mobile-Friendly**: Responsive design works on all devices
- **Category Tracking**: Separate counts for Men's and Women's categories

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Google Cloud Project** with Sheets API enabled
3. **Google Service Account** with access to your Google Sheet
4. **Google Sheet** with the following columns in row 1:
   - `timestamp` | `name` | `email` | `category` | `amount`

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd climb4good
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Google Sheets

1. Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Google Sheets API**
3. Create a **Service Account** (IAM & Admin → Service Accounts)
4. Download the JSON key file for your service account
5. Create a Google Sheet with columns: `timestamp`, `name`, `email`, `category`, `amount`
6. Share the sheet with your service account email (Editor permissions)

### 4. Configure Secrets

Copy the template and fill in your credentials:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with:
- Your Google service account JSON key (convert to TOML format)
- Your Google Sheet ID (from the sheet URL)
- Your Venmo handle for payment instructions

**Example conversion from JSON to TOML:**

Your service account JSON looks like:
```json
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "account@project.iam.gserviceaccount.com"
}
```

Convert to TOML in `secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "my-project"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "account@project.iam.gserviceaccount.com"
# ... include all other fields from JSON
```

### 5. Update Configuration

Edit `src/config.py` to customize:
- Event date and location
- Venmo handle (if not using secrets)
- Minimum donation amount
- Other app settings

### 6. Run Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud

1. Push your code to GitHub (make sure `.streamlit/secrets.toml` is NOT committed!)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. In the app settings, add your secrets (same TOML format as local)
6. Deploy!

## 📁 Project Structure

```
climb4good/
├── .streamlit/
│   ├── secrets.toml           # Your actual secrets (NOT committed)
│   └── secrets.toml.template  # Template for secrets
├── src/
│   ├── __init__.py
│   ├── config.py             # App configuration constants
│   └── sheets.py             # Google Sheets integration
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .gitignore
├── INSTRUCTIONS.md          # Detailed project specifications
└── README.md               # This file
```

## 🔧 Configuration Files

### `src/config.py`
Contains app constants like:
- Event details (date, location)
- Donation settings (minimum amount)
- Payment info (Venmo handle)
- Category options

### `src/sheets.py`
Google Sheets integration with functions:
- `get_sheets_client()` - Authenticate with Google Sheets API
- `append_registration()` - Add new registration to sheet
- `get_prize_pool_stats()` - Calculate totals and counts
- `get_recent_registrations()` - Fetch recent signups

## 🧪 Testing Checklist

Before going live, test:
- [ ] Form validates required fields (name, email, category, amount)
- [ ] Form rejects donations under minimum amount
- [ ] Successful registration writes to Google Sheet with timestamp
- [ ] Success message displays correct amount and Venmo handle
- [ ] Prize pool total calculates correctly
- [ ] Recent registrations display properly
- [ ] App works on mobile devices
- [ ] Error handling for Google Sheets API failures

## 🎨 Customization

### Styling
Edit the CSS in `app.py` to change colors, fonts, and layout. The current theme uses earthy/climbing colors (greens, browns).

### Payment Methods
Update the payment instructions in `app.py` and the Venmo handle in `src/config.py` or secrets.

### Categories
Modify `CATEGORY_OPTIONS` in `src/config.py` to add/change categories.

## 🐛 Troubleshooting

**"Failed to authenticate with Google Sheets"**
- Check that your service account JSON is correctly formatted in `secrets.toml`
- Verify the Google Sheets API is enabled in your GCP project
- Ensure the service account email has Editor access to your sheet

**"Failed to access worksheet"**
- Verify the spreadsheet ID in `secrets.toml` matches your sheet URL
- Check the worksheet name (tab name) is correct
- Confirm the sheet has the correct column headers

**"Registration not appearing in sheet"**
- Check that the sheet has columns: `timestamp`, `name`, `email`, `category`, `amount`
- Verify write permissions for the service account
- Look for error messages in the Streamlit logs

## 📝 License

MIT License - feel free to use this for your own climbing events!

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📞 Support

For issues or questions, please open a GitHub issue or contact the event organizers.

---

Built with ❤️ for the climbing community
