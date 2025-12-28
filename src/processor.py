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
    
    # Calculate FDR for the next 3 Gameweeks
    # Find the ID of the next upcoming Gameweek
    current_gw = next(event['id'] for event in raw_data['events'] if event['is_next'])
    next_3_gws = [current_gw, current_gw + 1, current_gw + 2]
    
    # Filter only upcoming fixtures for the relevant Gameweeks
    upcoming = fixtures_df[fixtures_df['event'].isin(next_3_gws)]
    
    team_fdr = {}
    for team_id in teams_map.keys():
        # Filter fixtures for the specific team (Home or Away)
        team_fixtures = upcoming[(upcoming['team_h'] == team_id) | (upcoming['team_a'] == team_id)]
        
        difficulties = []
        for _, row in team_fixtures.iterrows():
            if row['team_h'] == team_id:
                difficulties.append(row['team_h_difficulty'])
            else:
                difficulties.append(row['team_a_difficulty'])
        
        # Average difficulty for the next 3 games
        team_fdr[team_id] = sum(difficulties) / len(difficulties) if difficulties else 3

    # Add FDR score to each player based on their team
    players_df['next_3_fdr'] = players_df['team'].map(team_fdr)
    
    # Filtering: Only active players with significant minutes
    recommendations = players_df[(players_df['status'] == 'a') & (players_df['minutes'] > 450)]
    
    # Sort by high form (Desc) and easy fixtures (Asc)
    recommendations = recommendations.sort_values(by=['form', 'next_3_fdr'], ascending=[False, True])
    
    return recommendations[['web_name', 'team_name', 'form', 'next_3_fdr']].head(10)

if __name__ == "__main__":
    top_picks = process_data()
    print("--- FPL Smart Scout: Top Picks for Next 3 GWs ---")
    print(top_picks)
