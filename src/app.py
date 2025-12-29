import streamlit as st
from processor import process_data
from fetcher import fetch_fpl_data, fetch_fixtures
import pandas as pd

st.set_page_config(page_title="FPL Smart Scout", layout="wide")

# Sidebar Legend & Filters
st.sidebar.header("🎨 Legend & Settings")
st.sidebar.info("""
**Scout Score:** 🟢 High Score = Strong Pick  
**Next 3 FDR (Difficulty):** 🟢 Green (2.0) = Easy  
🟡 Yellow (3.0) = Average  
🔴 Red (4.0+) = Hard
""")

pos_filter = st.sidebar.selectbox("Position", ["All", "GKP", "DEF", "MID", "FWD"])
max_price = st.sidebar.slider("Max Price (£m)", 4.0, 15.0, 15.0, 0.5)

# Fetch Data
with st.spinner('Loading data from FPL...'):
    df = process_data()
    raw_data = fetch_fpl_data()
    fixtures = fetch_fixtures()

# --- 1. LEAGUE TABLE SECTION ---
st.title("🏆 FPL Smart Scout Dashboard")
with st.expander("View Premier League Table"):
    teams_df = pd.DataFrame(raw_data['teams'])
    # Sorting by position (rank) in the league
    league_table = teams_df[['name', 'position', 'played', 'win', 'draw', 'loss', 'goals_for', 'goals_against', 'points']].sort_values('position')
    league_table.columns = ['Team', 'Rank', 'P', 'W', 'D', 'L', 'GF', 'GA', 'Pts']
    st.dataframe(league_table, width="stretch", hide_index=True)

# --- 2. RECOMMENDATIONS TABLE ---
st.subheader(f"Top Recommendations: {pos_filter}")

# Filtering Logic
if pos_filter != "All":
    df = df[df['position'] == pos_filter]
filtered_df = df[df['now_cost'] <= max_price]

# Prepare Display (Added Team column as requested)
clean_display = filtered_df[[
    'web_name', 'team_name', 'now_cost', 'form', 'next_3_fdr', 'smart_score'
]].copy()

clean_display.columns = ['Player', 'Team', 'Price', 'Form', 'Next 3 FDR', 'Scout Score']

st.dataframe(
    clean_display.style.background_gradient(subset=['Scout Score'], cmap='Greens')
                       .background_gradient(subset=['Next 3 FDR'], cmap='RdYlGn_r')
                       .format({'Price': '£{:.1f}m', 'Scout Score': '{:.2f}', 'Next 3 FDR': '{:.2f}'}),
    width="stretch",
    hide_index=True
)

# --- 3. FIXTURES SECTION WITH FILTER ---
st.divider()
st.subheader("🗓️ Fixture List Analysis")

teams_map = {team['id']: team['name'] for team in raw_data['teams']}
fix_df = pd.DataFrame(fixtures)

# Dynamic GW Selection
all_upcoming_gws = sorted(fix_df[fix_df['finished'] == False]['event'].unique().tolist())
selected_gws = st.multiselect("Filter by Gameweek", options=all_upcoming_gws, default=all_upcoming_gws[:3])

upcoming = fix_df[fix_df['event'].isin(selected_gws)].copy()
upcoming['GW'] = upcoming['event']
upcoming['Date'] = pd.to_datetime(upcoming['kickoff_time']).dt.strftime('%d/%m %H:%M')
upcoming['Match'] = upcoming['team_h'].map(teams_map) + " vs " + upcoming['team_a'].map(teams_map)
upcoming['Difficulty (H/A)'] = upcoming['team_h_difficulty'].astype(str) + " / " + upcoming['team_a_difficulty'].astype(str)

st.dataframe(
    upcoming[['GW', 'Date', 'Match', 'Difficulty (H/A)']],
    width="stretch",
    hide_index=True
)
