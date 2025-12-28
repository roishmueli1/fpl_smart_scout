import streamlit as st
from processor import process_data

st.set_page_config(page_title="FPL Smart Scout", layout="wide")

st.title("⚽ FPL Smart Scout Dashboard")
st.write("Analyze the best players by position using the Smart Score algorithm.")

# Sidebar Filters
st.sidebar.header("Filters")
# User selects position
pos_filter = st.sidebar.selectbox("Select Position", ["All", "GKP", "DEF", "MID", "FWD"])
# User selects max price
max_price = st.sidebar.slider("Max Price (£m)", 4.0, 15.0, 15.0, 0.5)

with st.spinner('Updating data...'):
    df = process_data()

# Apply Filters
if pos_filter != "All":
    df = df[df['position'] == pos_filter]

filtered_df = df[df['now_cost'] <= max_price]

# Display Table
st.subheader(f"Top Recommendations: {pos_filter}")
st.dataframe(
    filtered_df.style.background_gradient(subset=['smart_score'], cmap='Greens'), 
    width="stretch"
)

# Metric Cards
if not filtered_df.empty:
    best = filtered_df.iloc[0]
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Pick", best['web_name'])
    c2.metric("Position", best['position'])
    c3.metric("Smart Score", round(best['smart_score'], 2))
