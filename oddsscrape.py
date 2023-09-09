import requests
import urllib
from datetime import datetime
import pandas as pd

BASE_URL = 'https://api.prop-odds.com'
API_KEY = 'lfRu8A34QwZVOmAfbTg1SMyha9dN46YCUzGgD60'

def get_request(url):
    response = requests.get(url)import requests
import urllib
from datetime import datetime
import pandas as pd

BASE_URL = 'https://api.prop-odds.com'
API_KEY = 'lfRu8A34QwZVOmAfbTg1SMyha9dN46YCUzGgD60'

def get_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    print('Request failed with status:', response.status_code)
    return {}

def get_mlb_games(date):
    query_params = {
        'date': date,
        'tz': 'America/Chicago',
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/games/mlb?' + params
    return get_request(url)

def get_game_info(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/game/' + game_id + '?' + params
    return get_request(url)

def get_markets(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/markets/' + game_id + '?' + params
    return get_request(url)

def get_most_recent_market_odds(game_id, market_name):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + f'/beta/odds/{game_id}/{market_name}?' + params
    return get_request(url)

def collect_market_data(game_id, market_name, player_name):
    odds_data = get_most_recent_market_odds(game_id, market_name)

    if 'sportsbooks' not in odds_data or len(odds_data['sportsbooks']) == 0:
        print(f'No odds found for game {game_id}, market {market_name}.')
        return []

    market_data = []

    outcomes = odds_data['sportsbooks'][0]['market']['outcomes']

    for outcome in outcomes:
        if 'Over' in outcome['name'] or 'Under' in outcome['name']:
            market_data.append({
                'game_id': game_id,
                'timestamp': outcome['timestamp'],
                'handicap': outcome['handicap'],
                'odds': outcome['odds'],
                'participant': outcome['participant'],
                'name': outcome['name'],
                'description': outcome['description'],
                'player_name': player_name  # Add the player_name column
            })

    return market_data

def main():
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    games = get_mlb_games(date)

    if len(games['games']) == 0:
        print('No games scheduled for today.')
        return

    # Create empty lists to collect the data
    pitcher_strikeout_data = []
    pitcher_walks_data = []

    for game in games['games']:
        game_id = game['game_id']
        game_info = get_game_info(game_id)
        markets = get_markets(game_id)

        if len(markets['markets']) == 0:
            print(f'No markets found for game {game_id}.')
            continue

        for market in markets['markets']:
            if market['name'] == 'pitcher_strikeout_over_under':
                pitcher_strikeout_data.extend(collect_market_data(game_id, market['name'], game_info['away_pitcher']['full_name']))
                pitcher_strikeout_data.extend(collect_market_data(game_id, market['name'], game_info['home_pitcher']['full_name']))
            elif market['name'] == 'pitcher_walks_over_under':
                pitcher_walks_data.extend(collect_market_data(game_id, market['name'], game_info['away_pitcher']['full_name']))
                pitcher_walks_data.extend(collect_market_data(game_id, market['name'], game_info['home_pitcher']['full_name']))

    if not pitcher_strikeout_data:
        print('No pitcher strikeout data found.')
    else:
        # Create a DataFrame from the collected data
        df_strikeout = pd.DataFrame(pitcher_strikeout_data)
        df_strikeout = df_strikeout[['game_id', 'timestamp', 'handicap', 'odds', 'participant', 'name', 'description', 'player_name']]
        df_strikeout.to_csv('pitcher_strikeout_data.csv', index=False)

    if not pitcher_walks_data:
        print('No pitcher walks data found.')
    else:
        # Create a DataFrame from the collected data
        df_walks = pd.DataFrame(pitcher_walks_data)
        df_walks = df_walks[['game_id', 'timestamp', 'handicap', 'odds', 'participant', 'name', 'description', 'player_name']]
        df_walks.to_csv('pitcher_walks_data.csv', index=False)

if __name__ == '__main__':
    main()

    if response.status_code == 200:
        return response.json()

    print('Request failed with status:', response.status_code)
    return {}

def get_mlb_games(date):
    query_params = {
        'date': date,
        'tz': 'America/Chicago',
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/games/mlb?' + params
    return get_request(url)

def get_game_info(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/game/' + game_id + '?' + params
    return get_request(url)

def get_markets(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/markets/' + game_id + '?' + params
    return get_request(url)

def get_most_recent_market_odds(game_id, market_name):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + f'/beta/odds/{game_id}/{market_name}?' + params
    return get_request(url)

def collect_market_data(game_id, market_name):
    odds_data = get_most_recent_market_odds(game_id, market_name)

    if 'sportsbooks' not in odds_data or len(odds_data['sportsbooks']) == 0:
        print(f'No odds found for game {game_id}, market {market_name}.')
        return []

    market_data = []

    outcomes = odds_data['sportsbooks'][0]['market']['outcomes']

    for outcome in outcomes:
        if 'Over' in outcome['name'] or 'Under' in outcome['name']:
            market_data.append({
                'game_id': game_id,
                'timestamp': outcome['timestamp'],
                'handicap': outcome['handicap'],
                'odds': outcome['odds'],
                'participant': outcome['participant'],
                'name': outcome['name'],
                'description': outcome['description']
            })

    return market_data

def main():
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    games = get_mlb_games(date)

    if len(games['games']) == 0:
        print('No games scheduled for today.')
        return

    # Create an empty list to collect the data
    pitcher_strikeout_data = []
    pitcher_walks_data = []

    for game in games['games']:
        game_id = game['game_id']
        game_info = get_game_info(game_id)
        markets = get_markets(game_id)

        if len(markets['markets']) == 0:
            print(f'No markets found for game {game_id}.')
            continue

        for market in markets['markets']:
            if market['name'] == 'pitcher_strikeout_over_under':
                pitcher_strikeout_data.extend(collect_market_data(game_id, market['name']))
            elif market['name'] == 'pitcher_walks_over_under':
                pitcher_walks_data.extend(collect_market_data(game_id, market['name']))

    if not pitcher_strikeout_data:
        print('No pitcher strikeout data found.')
    else:
        # Create a DataFrame from the collected data
        df_strikeout = pd.DataFrame(pitcher_strikeout_data)
        df_strikeout = df_strikeout[['game_id', 'timestamp', 'handicap', 'odds', 'participant', 'name', 'description']]
        df_strikeout.to_csv('pitcher_strikeout_data.csv', index=False)

    if not pitcher_walks_data:
        print('No pitcher walks data found.')
    else:
        # Create a DataFrame from the collected data
        df_walks = pd.DataFrame(pitcher_walks_data)
        df_walks = df_walks[['game_id', 'timestamp', 'handicap', 'odds', 'participant', 'name', 'description']]
        df_walks.to_csv('pitcher_walks_data.csv', index=False)

if __name__ == '__main__':
    main()