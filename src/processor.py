import pandas as pd
from fetcher import fetch_fpl_data, fetch_fixtures

def process_data():
    # Load raw data from API functions
    raw_data = fetch_fpl_data()
    fixtures = fetch_fixtures()
    
    # Initialize DataFrames
    players_df = pd.DataFrame(raw_data['elements'])
    teams_df = pd.DataFrame(raw_data['teams'])
    fixtures_df = pd.DataFrame(fixtures)
    
    # Map team IDs to team names
    teams_map = teams_df.set_index('id')['name'].to_dict()
    players_df['team_name'] = players_df['team'].map(teams_map)
    
    # Data Cleaning: Convert price and numeric fields
    players_df['now_cost'] = players_df['now_cost'] / 10
    players_df['form'] = pd.to_numeric(players_df['form'])
    players_df['total_points'] = pd.to_numeric(players_df['total_points'])
    
    # Calculate FDR for the next 3 Gameweeks
    current_gw = next(event['id'] for event in raw_data['events'] if event['is_next'])
    next_3_gws = [current_gw, current_gw + 1, current_gw + 2]
    upcoming = fixtures_df[fixtures_df['event'].isin(next_3_gws)]
    
    team_fdr = {}
    for team_id in teams_map.keys():
        team_fixtures = upcoming[(upcoming['team_h'] == team_id) | (upcoming['team_a'] == team_id)]
        difficulties = []
        for _, row in team_fixtures.iterrows():
            if row['team_h'] == team_id:
                difficulties.append(row['team_h_difficulty'])
            else:
                difficulties.append(row['team_a_difficulty'])
        team_fdr[team_id] = sum(difficulties) / len(difficulties) if difficulties else 3

    # Add FDR score to each player
    players_df['next_3_fdr'] = players_df['team'].map(team_fdr)
    
    # Calculate Value Metric (Points per Million)
    players_df['value_season'] = players_df['total_points'] / players_df['now_cost']
    
    # --- SMART SCORE LOGIC ---
    # Normalize values to 0-1 range for fair weighting
    # We want low FDR to be a high score, so we use (5 - FDR)
    fdr_inverted = 5 - players_df['next_3_fdr'] 
    
    # Weighting: 50% Form, 30% Fixtures, 20% Seasonal Value
    players_df['smart_score'] = (
        (players_df['form'] * 0.5) + 
        (fdr_inverted * 0.3) + 
        (players_df['value_season'] * 0.2)
    )
    
    # Filtering: Only available players with significant playing time
    recommendations = players_df[(players_df['status'] == 'a') & (players_df['minutes'] > 450)]
    
    # Sort by the final Smart Score
    recommendations = recommendations.sort_values(by='smart_score', ascending=False)
    
    return recommendations[['web_name', 'team_name', 'now_cost', 'form', 'next_3_fdr', 'smart_score']].head(10)

if __name__ == "__main__":
    top_picks = process_data()
    print("--- FPL Smart Scout: Top Picks Based on Smart Score ---")
    print(top_picks)
