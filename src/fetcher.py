import requests

def fetch_fpl_data():
    """Fetch general data from the main FPL API endpoint"""
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    return response.json()

def fetch_fixtures():
    """Fetch the full list of fixtures for the season"""
    url = "https://fantasy.premierleague.com/api/fixtures/"
    response = requests.get(url)
    return response.json()
