import requests
import json
from datetime import datetime

from const import *

def google_news_GET(topic, news_type):
    url = "https://google-news13.p.rapidapi.com/search"
    querystring = {"keyword":str(topic) + " " + str(news_type),"lr":"en-US"}
    headers = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "google-news13.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    all_response = response.json()
    top_5_responses = all_response['items'][:1]  # Assuming 'articles' is the key for the list of articles
    return top_5_responses

def chat_gpt_GET(word):
    ("testing123: " + str(word))
    url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "Please summarise " +  str(word) + " in a few lines for a novice to the game of football"
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }
    response = requests.post(url, json=payload, headers=headers)

    data  = json.dumps(response.json())
    data2 = json.loads(data)
    return data2['choices'][0]['message']['content']

def large_language_model_classifier(article):

    all_categories = leagues + premier_league_teams + bundesliga_teams + la_liga_teams + serie_a_teams + ligue_1_teams + mls_teams + content

    # Convert the list to a string separated by commas
    categories_string = ", ".join(all_categories)

    url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"Can you take in a news article and classify it into as many of these categories as you see fit that are relavent to the article's information (but the maximum is 5 categories). But only return a string of categories separated by commas: {categories_string}"
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }
    response = requests.post(url, json=payload, headers=headers)

    data  = json.dumps(response.json())
    data2 = json.loads(data)
    #print(data2)
    return data2['choices'][0]['message']['content']

def team_statistics_GET(team_id):
    # Get League standings for Liverpool
    url_leagueStandings = "https://api-football-v1.p.rapidapi.com/v3/standings"
    querystring_leagueStandings = {"season":"2023","team":team_id}
    headers = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response_leagueStandings = requests.get(url_leagueStandings, headers=headers, params=querystring_leagueStandings)
    #print(response_leagueStandings.json())

    data = json.dumps(response_leagueStandings.json())
    parsed_data = json.loads(data)

    print(parsed_data)

    # Extract Premier League information
    premier_league_info = parsed_data['response'][1]['league']

    # Extract team standing
    team_standing = premier_league_info['standings'][0][0]

    # Extract relevant information
    league_name = premier_league_info['name']
    league_position = team_standing['rank']
    total_points = team_standing['points']
    goal_difference = team_standing['goalsDiff']
    total_matches_played = team_standing['all']['played']
    matches_won = team_standing['all']['win']
    matches_lost = team_standing['all']['lose']
    matches_drawn = team_standing['all']['draw']

    # Print extracted information
    print("Premier League Information:")
    print("League Name:", league_name)
    print("League Position:", league_position)
    print("Total Points:", total_points)
    print("Goal Difference:", goal_difference)
    print("Total Matches Played:", total_matches_played)
    print("Matches Won:", matches_won)
    print("Matches Lost:", matches_lost)
    print("Matches Drawn:", matches_drawn)

    
    title = "Team statistics news"
    description = "see how this team is currently doing in the league and their statistics this season"

    return league_name, league_position, total_points, goal_difference, total_matches_played, matches_won, matches_lost, matches_drawn

def team_recent_transfers_GET(team_id):
    url_transfer = "https://api-football-v1.p.rapidapi.com/v3/transfers"

    querystring_transfer = {"team":team_id}

    headers_transfer = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response_transfer = requests.get(url_transfer, headers=headers_transfer, params=querystring_transfer)
    print(response_transfer.json())

    # Parse JSON response
    data_pre = json.dumps(response_transfer.json())
    data = json.loads(data_pre)

    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return datetime.strptime(date_str, '%d%m%y')

   # Sort players based on their earliest transfer date
    sorted_players = sorted(data['response'], key=lambda x: parse_date(x['transfers'][0]['date']))

    print(sorted_players)

    # Retrieve the 3 most recent transfers
    #recent_transfers = data['response'][-5:]
    recent_transfers = sorted_players[-5:]

    # Iterate over recent transfers and store required information
    transfer_info = []
    for transfer in recent_transfers:
        player_id = transfer['player']['id']
        player_name = transfer['player']['name']
        transfer_date = datetime.fromisoformat(transfer['transfers'][0]['date'])
        transfer_type = transfer['transfers'][0]['type']
        incoming_team_name = transfer['transfers'][0]['teams']['in']['name']
        incoming_team_logo = transfer['transfers'][0]['teams']['in']['logo']
        outgoing_team_name = transfer['transfers'][0]['teams']['out']['name']
        outgoing_team_logo = transfer['transfers'][0]['teams']['out']['logo']

        transfer_info.append({
            'ID': player_id,
            'Name': player_name,
            'Transfer Date': transfer_date,
            'Type': transfer_type,
            'Incoming Team Name': incoming_team_name,
            'Incoming Team Logo': incoming_team_logo,
            'Outgoing Team Name': outgoing_team_name,
            'Outgoing Team Logo': outgoing_team_logo
        })

    # Print transfer information
    for transfer in transfer_info:
        print(transfer)

    return transfer_info

def team_recent_injuries_GET(team_id):
    url_injury = "https://api-football-v1.p.rapidapi.com/v3/injuries"
    querystring_injury = {"season":"2023","team":team_id}
    headers_injury = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response_injury = requests.get(url_injury, headers=headers_injury, params=querystring_injury)
    
    print(response_injury.json())

    # Parse JSON response
    data_pre = json.dumps(response_injury.json())
    data = json.loads(data_pre)

    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return datetime.strptime(date_str, '%d%m%y')

   # Sort players based on their earliest transfer date
    sorted_players = sorted(data['response'], key=lambda x: x['fixture']['timestamp'])

    # Retrieve the 3 most recent transfers
    #recent_transfers = data['response'][-5:]
    recent_injuries = sorted_players[-5:]

    #print(recent_injuries)

    # Extracting information
    injured_players = []
    for entry in recent_injuries:
        player_name = entry['player']['name']
        injury_reason = entry['player']['reason']
        fixture_details = entry['league']['name']
        fixture_date_time = entry['fixture']['date']
        
        injured_players.append({
            'Player Name': player_name,
            'Injury Reason': injury_reason,
            'Fixture Details': fixture_details,
            'Fixture Date/Time': fixture_date_time
        })

    print(injured_players)

    return injured_players

def team_lastest_score_GET(team_id):
    # -- Get Latest Fixture for Liverpool --
    url_test = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring_test = {"last":"1", "team":team_id}
    headers_test = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response_test = requests.get(url_test, headers=headers_test, params=querystring_test)

    # Parse JSON data
    data  = json.dumps(response_test.json())
    parsed_data = json.loads(data)
    # Get the fixture ID
    fixture_id = parsed_data['response'][0]['fixture']['id']

    url1 = "https://api-football-v1.p.rapidapi.com/v3/fixtures/events"
    querystring1 = {"fixture":fixture_id}
    headers1 = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response1 = requests.get(url1, headers=headers1, params=querystring1)
   
    data  = json.dumps(response1.json())
    parsed_data = json.loads(data)

    print(parsed_data)

    score = ""
    home_goals = []
    away_goals = []
    home_red_cards = []
    away_red_cards = []
    home_yellow_cards = []
    away_yellow_cards = []

    home_team_name = ""
    away_team_name = ""

    for event in parsed_data['response']:
        if event['team']['id'] != team_id:  # Assuming 40 is the ID of the home team
            away_team_name = event['team']['name']
        else:
            home_team_name = event['team']['name']

    print("home team: " + str(home_team_name))
    print("away team: " + str(away_team_name))

    # Iterate over the response data
    for event in parsed_data['response']:
        # Extract event details
        event_type = event['type']
        player_name = event['player']['name']
        team_name = event['team']['name']
        current_team_id = event['team']['id']
        
        # Check event type
        if event_type == 'Goal':
            if current_team_id == team_id:
                home_goals.append(player_name)
            else:
                away_goals.append(player_name)
        elif event_type == 'Card':
            card_detail = event['detail']
            if card_detail == 'Yellow Card':
                if current_team_id == team_id:
                    home_yellow_cards.append(player_name)
                else:
                    away_yellow_cards.append(player_name)
            elif card_detail == 'Red Card':
                if current_team_id == team_id:
                    home_red_cards.append(player_name)
                else:
                    away_red_cards.append(player_name)

    score = home_team_name +  ": " + str(len(home_goals)) + " - " + away_team_name +  ": " + str(len(away_goals))

    # Print goal scorers, red cards, and yellow cards for each team
    print("Liverpool Goal Scorers:", home_goals)
    print("Opponent Goal Scorers:", away_goals)
    print("Liverpool Red Cards:", home_red_cards)
    print("Opponent Red Cards:", away_red_cards)
    print("Liverpool Yellow Cards:", home_yellow_cards)
    print("Opponent Yellow Cards:", away_yellow_cards)

    return home_team_name, away_team_name, score, home_goals, away_goals, home_red_cards, away_red_cards, home_yellow_cards, away_yellow_cards

def team_id_GET(team_name):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    headers = {
        "X-RapidAPI-Key": "f9ad3cd1bdmsh63ce9f557ee648ap1d00c6jsn7d3a27193a51",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    params = {
        "name": team_name
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    print(data)
    if data['response']:
        return data['response'][0]['team']['id']
    else:
        return None