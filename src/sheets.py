"""Google Sheets integration for reading/writing registration data."""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import logging

from src.config import WORKSHEET_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


@st.cache_resource
def get_sheets_client():
    """
    Get an authenticated gspread client using service account credentials.
    
    Returns:
        gspread.Client: Authenticated client for Google Sheets API
    """
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        logger.info("Successfully authenticated with Google Sheets API")
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        raise


def get_worksheet():
    """Get the worksheet object for reading/writing."""
    try:
        client = get_sheets_client()
        spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
        worksheet_name = st.secrets["sheets"].get("worksheet_name", WORKSHEET_NAME)
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except Exception as e:
        logger.error(f"Failed to access worksheet: {e}")
        raise


def append_registration(name: str, email: str, category: str, amount: float) -> bool:
    """
    Append a new registration row to the Google Sheet.
    
    Args:
        name: Participant name or pseudonym
        email: Participant email
        category: Competition category (Men/Women)
        amount: Intended donation amount
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        worksheet = get_worksheet()
        timestamp = datetime.now().isoformat()
        
        row = [timestamp, name, email, category, amount]
        worksheet.append_row(row)
        
        # Clear the cache so stats update immediately
        get_all_registrations.clear()
        
        logger.info(f"Successfully registered: {name} ({category}) - ${amount}")
        return True
    except Exception as e:
        logger.error(f"Failed to append registration: {e}")
        return False


@st.cache_data(ttl=60)
def get_all_registrations() -> pd.DataFrame:
    """
    Fetch all registrations from the Google Sheet.
    
    Returns:
        pd.DataFrame: All registration data with columns: 
                      timestamp, name, email, category, amount
    """
    try:
        worksheet = get_worksheet()
        data = worksheet.get_all_values()
        
        if len(data) <= 1:  # Only header or empty
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=["timestamp", "name", "email", "category", "amount"])
        
        # Create DataFrame (first row is header)
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Convert amount to numeric
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        
        logger.info(f"Fetched {len(df)} registrations from sheet")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch registrations: {e}")
        # Return empty DataFrame on error
        return pd.DataFrame(columns=["timestamp", "name", "email", "category", "amount"])


@st.cache_data(ttl=60)
def get_prize_pool_stats() -> Dict[str, any]:
    """
    Calculate prize pool statistics from all registrations.
    
    Returns:
        dict: Statistics including:
            - total_amount: Sum of all pledged donations
            - participant_count: Total number of registrations
            - men_count: Number of Men's category registrations
            - women_count: Number of Women's category registrations
    """
    df = get_all_registrations()
    
    if df.empty:
        return {
            "total_amount": 0,
            "participant_count": 0,
            "men_count": 0,
            "women_count": 0
        }
    
    stats = {
        "total_amount": df["amount"].sum(),
        "participant_count": len(df),
        "men_count": len(df[df["category"] == "Men"]),
        "women_count": len(df[df["category"] == "Women"])
    }
    
    logger.info(f"Prize pool stats: ${stats['total_amount']:.2f}, {stats['participant_count']} participants")
    return stats


def get_recent_registrations(limit: int = 10) -> pd.DataFrame:
    """
    Get the most recent registrations.
    
    Args:
        limit: Number of recent registrations to return
        
    Returns:
        pd.DataFrame: Recent registrations (newest first)
    """
    df = get_all_registrations()
    
    if df.empty:
        return df
    
    # Return most recent registrations (last rows in sheet)
    return df.tail(limit).iloc[::-1]  # Reverse to show newest first
