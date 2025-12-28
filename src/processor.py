import pandas as pd
from fetcher import fetch_fpl_data, fetch_fixtures

def process_data():
    """Main processing function to clean data and calculate the Smart Score"""
    # Fetch raw data from the API functions in fetcher.py
    raw_data = fetch_fpl_data()
    fixtures = fetch_fixtures()
    
    players_df = pd.DataFrame(raw_data['elements'])
    fixtures_df = pd.DataFrame(fixtures)
    
    # 1. AUTHENTICATE CURRENT TIME: Identify the upcoming Gameweek (GW)
    # FPL API uses 'is_next': True to mark the next active GW
    try:
        current_gw = next(event['id'] for event in raw_data['events'] if event['is_next'])
    except StopIteration:
        # Fallback to GW 1 if the API doesn't return a 'next' event
        current_gw = 1

    # 2. FIXTURE VALIDATION: Analyze the next 3 Gameweeks
    # Filter only fixtures that haven't finished yet
    next_3_gws = [current_gw, current_gw + 1, current_gw + 2]
    upcoming_fixtures = fixtures_df[
        (fixtures_df['event'].isin(next_3_gws)) & 
        (fixtures_df['finished'] == False)
    ]

    # 3. ACCURATE FDR CALCULATION (Fixture Difficulty Rating)
    # Map team IDs to their real names
    teams_map = {team['id']: team['name'] for team in raw_data['teams']}
    team_fdr = {}

    for team_id in teams_map.keys():
        # Filter matches where the team is either Home (team_h) or Away (team_a)
        relevant_matches = upcoming_fixtures[
            (upcoming_fixtures['team_h'] == team_id) | 
            (upcoming_fixtures['team_a'] == team_id)
        ]
        
        difficulties = []
        for _, row in relevant_matches.iterrows():
            # Check if the team is home or away to get the correct difficulty
            if row['team_h'] == team_id:
                difficulties.append(row['team_h_difficulty'])
            else:
                difficulties.append(row['team_a_difficulty'])
        
        # Blank Gameweek Handling: If a team has NO games, assign high difficulty (5.0)
        # Otherwise, calculate the mean difficulty
        team_fdr[team_id] = sum(difficulties) / len(difficulties) if difficulties else 5.0

    # 4. MERGE DATA AND CALCULATE METRICS
    players_df['team_name'] = players_df['team'].map(teams_map)
    players_df['next_3_fdr'] = players_df['team'].map(team_fdr)
    
    # Clean numeric fields
    players_df['form'] = pd.to_numeric(players_df['form'])
    players_df['now_cost'] = players_df['now_cost'] / 10
    players_df['total_points'] = pd.to_numeric(players_df['total_points'])
    
    # Calculate Value metric (Points per Million)
    players_df['value_season'] = players_df['total_points'] / players_df['now_cost']
    
    # SMART SCORE CALCULATION: 50% Form, 30% Fixtures (Inverted), 20% Value
    # FDR is inverted (5-FDR) because a lower FDR means an easier game
    fdr_inverted = 5 - players_df['next_3_fdr']
    players_df['smart_score'] = (
        (players_df['form'] * 0.5) + 
        (fdr_inverted * 0.3) + 
        (players_df['value_season'] * 0.2)
    )
    
    # Map position codes to names
    position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    players_df['position'] = players_df['element_type'].map(position_map)
    
    # 5. FINAL FILTERING
    # Only available players with more than 450 minutes played
    res = players_df[(players_df['status'] == 'a') & (players_df['minutes'] > 450)]
    
    return res.sort_values(by='smart_score', ascending=False)

if __name__ == "__main__":
    # Test execution
    data = process_data()
    print(data[['web_name', 'team_name', 'position', 'smart_score']].head(10))
