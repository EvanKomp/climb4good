"""
Climb for Charity: Registration & Prize Pool Tracker
A Streamlit app for managing charity climbing event registrations.
"""

import streamlit as st
import time
from datetime import datetime

from src.config import (
    APP_TITLE,
    EVENT_DATE,
    EVENT_LOCATION,
    MINIMUM_DONATION,
    DEFAULT_DONATION,
    VENMO_HANDLE,
    CATEGORY_OPTIONS,
    PRIZE_POOL_REFRESH_INTERVAL,
    RECENT_REGISTRATIONS_COUNT
)
from src.sheets import (
    append_registration,
    get_prize_pool_stats,
    get_recent_registrations,
    get_all_registrations
)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Large prize pool display */
    .prize-pool-total {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        margin: 1rem 0;
    }
    
    /* Stats cards */
    .stat-card {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1976D2;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Registration success box */
    .success-box {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Recent registration item */
    .recent-reg {
        padding: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 1rem 0;
        color: #2E7D32;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown(f"<h1 class='app-header'>🧗 {APP_TITLE}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666;'>{EVENT_LOCATION} • {EVENT_DATE}</p>", unsafe_allow_html=True)

# Event details link
st.markdown("""
<div style='text-align: center; margin: 1rem 0; padding: 1rem; background: #FFF3E0; border-radius: 8px; border: 2px solid #FF9800;'>
    <a href='https://docs.google.com/document/d/14ApFwi1OltOzjyrp9BH0jYNyKPl59_yaLcUskE4LfIs/edit?usp=sharing' 
       target='_blank' 
       style='font-size: 1.2rem; font-weight: bold; color: #E65100; text-decoration: none;'>
        📋 VIEW FULL EVENT DETAILS & INFO →
    </a>
</div>
""", unsafe_allow_html=True)

# Initialize session state for form reset
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False
if "registered_amount" not in st.session_state:
    st.session_state.registered_amount = 0

# Create tabs
tab1, tab2 = st.tabs(["📝 Register", "💰 Prize Pool"])

# ==================== REGISTRATION TAB ====================
with tab1:
    st.header("Register for the Event")
    
    if st.session_state.registration_success:
        # Show success message and payment instructions
        st.success("🎉 You're registered!")
        
        st.markdown(f"""
        <div class='success-box'>
        <h3>💰 Now complete your donation!</h3>
        <p><strong>You pledged: ${st.session_state.registered_amount:.2f}</strong></p>
        
        <p><strong>Pay via Venmo: {VENMO_HANDLE}</strong><br>
        <em>Write note as: "Climb4Good - Your Name"</em></p>
        
        <p style='text-align: center; margin: 1rem 0;'>— OR —</p>
        
        <p>Bring cash to the event and pay at check-in.</p>
        
        <p><em>Your pledge is counting toward our prize pool total!</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Check out the Prize Pool tab above to see your contribution added to the total!**")
        
        st.info(f"**Event Details**\n\n📅 Date: {EVENT_DATE}\n\n📍 Location: {EVENT_LOCATION}")
        
        if st.button("Register Another Person"):
            st.session_state.registration_success = False
            st.session_state.registered_amount = 0
            st.rerun()
    else:
        # Show registration form
        st.markdown("""
        Join us for a day of climbing and community! All donations go toward the prize pool,
        which will be split between the Men's and Women's category winners.
        """)
        
        with st.form("registration_form"):
            # Name field
            name = st.text_input(
                "Name or Pseudonym *",
                placeholder="Enter your name or a fun pseudonym",
                help="This will be displayed publicly in recent registrations"
            )
            
            # Email field
            email = st.text_input(
                "Email Address *",
                placeholder="your@email.com",
                help="For event updates and confirmation only"
            )
            
            # Category selection
            category = st.radio(
                "Competition Category *",
                options=CATEGORY_OPTIONS,
                help="Non-binary participants can choose which group to compete in"
            )
            
            # Donation amount
            amount = st.number_input(
                "Pledge Amount ($) *",
                min_value=MINIMUM_DONATION,
                value=DEFAULT_DONATION,
                step=5,
                help=f"This is for prize pool tracking only — you'll pay separately via Venmo or cash at the event. Minimum ${MINIMUM_DONATION}, more is always welcome!"
            )
            
            # Submit button
            submitted = st.form_submit_button("🧗 Register for Climb4Good")
            
            if submitted:
                # Validation
                errors = []
                
                if not name or len(name) < 2:
                    errors.append("Name must be at least 2 characters long")
                if len(name) > 50:
                    errors.append("Name must be less than 50 characters")
                
                if not email or "@" not in email:
                    errors.append("Please enter a valid email address")
                
                if amount < MINIMUM_DONATION:
                    errors.append(f"Minimum donation is ${MINIMUM_DONATION}")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Attempt to register
                    with st.spinner("Registering..."):
                        success = append_registration(name, email, category, amount)
                    
                    if success:
                        st.session_state.registration_success = True
                        st.session_state.registered_amount = amount
                        st.rerun()
                    else:
                        st.error("❌ Registration failed. Please try again or email komp.evan@gmail.com for assistance.")

# ==================== PRIZE POOL TAB ====================
with tab2:
    st.header("Pledged Prize Pool")
    
    # Auto-refresh container
    prize_pool_container = st.empty()
    
    with prize_pool_container.container():
        # Get stats
        try:
            stats = get_prize_pool_stats()
            
            # Display large total
            st.markdown(
                f"<div class='prize-pool-total'>${stats['total_amount']:,.2f}</div>",
                unsafe_allow_html=True
            )
            
            st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>Total Pledged Donations</p>", unsafe_allow_html=True)
            
            # Display participant stats in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{stats['participant_count']}</div>
                    <div class='stat-label'>Total Climbers</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{stats['men_count']}</div>
                    <div class='stat-label'>Men's Category</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{stats['women_count']}</div>
                    <div class='stat-label'>Women's Category</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Recent registrations
            st.markdown("---")
            st.subheader("Recent Registrations")
            
            recent = get_recent_registrations(RECENT_REGISTRATIONS_COUNT)
            
            if not recent.empty:
                for _, row in recent.iterrows():
                    category_emoji = "🧗‍♂️" if row["category"] == "Men" else "🧗‍♀️"
                    st.markdown(
                        f"<div class='recent-reg'>{category_emoji} <strong>{row['name']}</strong> joined!</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("No registrations yet. Be the first to register!")
            
            # Last updated timestamp
            st.markdown(
                f"<p style='text-align: center; color: #999; font-size: 0.8rem; margin-top: 2rem;'>Last updated: {datetime.now().strftime('%I:%M:%S %p')}</p>",
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error("Unable to load prize pool data. Please check your internet connection.")
            st.caption(f"Error: {str(e)}")
    
    # Auto-refresh button
    if st.button("🔄 Refresh Now"):
        # Clear caches to force fresh data
        get_prize_pool_stats.clear()
        get_all_registrations.clear()
        st.rerun()
    
    st.info(f"💡 This page automatically refreshes every {PRIZE_POOL_REFRESH_INTERVAL} seconds")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 0.8rem;'>Built with ❤️ for the climbing community</p>",
    unsafe_allow_html=True
)
