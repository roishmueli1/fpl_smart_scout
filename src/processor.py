import pandas as pd
from fetcher import fetch_fpl_data, fetch_fixtures

def process_data():
    raw_data = fetch_fpl_data()
    fixtures = fetch_fixtures()
    
    players_df = pd.DataFrame(raw_data['elements'])
    teams_df = pd.DataFrame(raw_data['teams'])
    fixtures_df = pd.DataFrame(fixtures)
    
    # Map team IDs to team names
    teams_map = teams_df.set_index('id')['name'].to_dict()
    players_df['team_name'] = players_df['team'].map(teams_map)
    
    # NEW: Map element_type to actual position names
    position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    players_df['position'] = players_df['element_type'].map(position_map)
    
    # Data Cleaning
    players_df['now_cost'] = players_df['now_cost'] / 10
    players_df['form'] = pd.to_numeric(players_df['form'])
    players_df['total_points'] = pd.to_numeric(players_df['total_points'])
    
    # FDR Calculation
    current_gw = next(event['id'] for event in raw_data['events'] if event['is_next'])
    next_3_gws = [current_gw, current_gw + 1, current_gw + 2]
    upcoming = fixtures_df[fixtures_df['event'].isin(next_3_gws)]
    
    team_fdr = {}
    for team_id in teams_map.keys():
        team_fixtures = upcoming[(upcoming['team_h'] == team_id) | (upcoming['team_a'] == team_id)]
        difficulties = [row['team_h_difficulty'] if row['team_h'] == team_id else row['team_a_difficulty'] for _, row in team_fixtures.iterrows()]
        team_fdr[team_id] = sum(difficulties) / len(difficulties) if difficulties else 3

    players_df['next_3_fdr'] = players_df['team'].map(team_fdr)
    players_df['value_season'] = players_df['total_points'] / players_df['now_cost']
    
    # Smart Score Calculation
    fdr_inverted = 5 - players_df['next_3_fdr']
    players_df['smart_score'] = (players_df['form'] * 0.5) + (fdr_inverted * 0.3) + (players_df['value_season'] * 0.2)
    
    # Filtering
    recommendations = players_df[(players_df['status'] == 'a') & (players_df['minutes'] > 450)]
    recommendations = recommendations.sort_values(by='smart_score', ascending=False)
    
    # Added 'position' to the returned columns
    return recommendations[['web_name', 'team_name', 'position', 'now_cost', 'form', 'next_3_fdr', 'smart_score']]
