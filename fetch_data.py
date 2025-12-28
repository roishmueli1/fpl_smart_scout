import requests
import pandas as pd

def main():
    # כתובת ה-API הרשמית של FPL
    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    
    print("Fetching data from FPL API...")
    response = requests.get(URL)
    data = response.json()
    
    # שליפת רשימת השחקנים מתוך ה-JSON
    players = data['elements']
    
    # המרה לטבלת פנדאס לצורך ניתוח נוח
    df = pd.DataFrame(players)
    
    # הצגת 5 השורות הראשונות עם עמודות נבחרות (שם, מחיר, נקודות)
    print(df[['web_name', 'now_cost', 'total_points']].head())

if __name__ == "__main__":
    main()
