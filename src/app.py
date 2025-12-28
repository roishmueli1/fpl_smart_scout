import streamlit as st
from processor import process_data

# Set page configuration
st.set_page_config(page_title="FPL Smart Scout", layout="wide")

# Main Title
st.title("⚽ FPL Smart Scout Dashboard")
st.write("Real-time player recommendations based on Form, FDR, and Value.")

# Sidebar for filters
st.sidebar.header("Filters")
# User can filter by maximum price
max_price = st.sidebar.slider("Max Price (£m)", 4.0, 15.0, 15.0, 0.5)

# Fetch and analyze Data
with st.spinner('Fetching and analyzing FPL data...'):
    df = process_data()

# Apply filters based on sidebar input
filtered_df = df[df['now_cost'] <= max_price]

# Display Top Picks
st.subheader("Top Recommended Picks (Next 3 GWs)")

# Display dataframe with background gradient styling
# Using width="stretch" as required by 2025 Streamlit updates
st.dataframe(
    filtered_df.style.background_gradient(subset=['smart_score'], cmap='Greens'), 
    width="stretch"
)

# Metric cards for the #1 recommended player
if not filtered_df.empty:
    best_player = filtered_df.iloc[0]
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Pick", best_player['web_name'])
    col2.metric("Smart Score", round(best_player['smart_score'], 2))
    col3.metric("Team", best_player['team_name'])

# Footer information about the algorithm
st.info("The Smart Score is calculated based on: 50% Form, 30% Fixture Ease (Inverted FDR), and 20% Seasonal Value.")
