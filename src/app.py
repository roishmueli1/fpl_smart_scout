import streamlit as st
from processor import process_data
from fetcher import fetch_fpl_data, fetch_fixtures
import pandas as pd

st.set_page_config(page_title="FPL Smart Scout", layout="wide")

st.title("⚽ FPL Smart Scout")

# Sidebar Filters
st.sidebar.header("Settings")
pos_filter = st.sidebar.selectbox("Position", ["All", "GKP", "DEF", "MID", "FWD"])
max_price = st.sidebar.slider("Max Price (£m)", 4.0, 15.0, 15.0, 0.5)

# Fetch Data
with st.spinner('Loading...'):
    df = process_data()
    raw_data = fetch_fpl_data()
    fixtures = fetch_fixtures()

# Filtering
if pos_filter != "All":
    df = df[df['position'] == pos_filter]
filtered_df = df[df['now_cost'] <= max_price]

# --- 1. CLEAN RECOMMENDATION TABLE ---
st.subheader(f"Top Recommendations: {pos_filter}")

# Showing only requested columns: Name, Price, and Recommendation (Smart Score)
clean_display = filtered_df[['web_name', 'now_cost', 'smart_score']].copy()
clean_display.columns = ['Player', 'Price (£m)', 'Scout Score']

st.dataframe(
    clean_display.style.background_gradient(subset=['Scout Score'], cmap='Greens'), 
    width="stretch",
    hide_index=True
)

# --- 2. FULL FIXTURES SECTION ---
st.divider()
st.subheader("🗓️ Full Fixture List (Next 3 GWs)")

# Preparing fixture data for display
teams_map = {team['id']: team['name'] for team in raw_data['teams']}
fix_df = pd.DataFrame(fixtures)

# Identify upcoming GWs
try:
    current_gw = next(event['id'] for event in raw_data['events'] if event['is_next'])
except:
    current_gw = 1

next_3 = [current_gw, current_gw+1, current_gw+2]
upcoming = fix_df[fix_df['event'].isin(next_3)].copy()

# Format the fixtures table
upcoming['GW'] = upcoming['event']
upcoming['Date'] = pd.to_datetime(upcoming['kickoff_time']).dt.strftime('%d/%m %H:%M')
upcoming['Match'] = upcoming['team_h'].map(teams_map) + " vs " + upcoming['team_a'].map(teams_map)
upcoming['Difficulty (H/A)'] = upcoming['team_h_difficulty'].astype(str) + " / " + upcoming['team_a_difficulty'].astype(str)

st.dataframe(
    upcoming[['GW', 'Date', 'Match', 'Difficulty (H/A)']],
    width="stretch",
    hide_index=True
)
