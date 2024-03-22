import pandas as pd
import random

# Load the Excel file
excel_file = pd.ExcelFile('ncaa.xlsx')

# Create dataframes from each tab
key_value_pairs = pd.read_excel(excel_file, 'seedrecords')
westteams_df = pd.read_excel(excel_file, 'westteams')
eastteams_df = pd.read_excel(excel_file, 'eastteams')
midwestteams_df = pd.read_excel(excel_file, 'midwestteams')
southteams_df = pd.read_excel(excel_file, 'southteams')

# Mapping the seed from each region to the corresponding value
seed_to_value_map = key_value_pairs.set_index('Key')['Value'].to_dict()

# Mapping the seed to team
west_seed_to_team_map = westteams_df.set_index('Seed')['Team'].to_dict()
east_seed_to_team_map = eastteams_df.set_index('Seed')['Team'].to_dict()
midwest_seed_to_team_map = midwestteams_df.set_index('Seed')['Team'].to_dict()
south_seed_to_team_map = southteams_df.set_index('Seed')['Team'].to_dict()

# Define the simulate_matchup function using the seed_to_value_map
def simulate_matchup(team1_seed, team2_seed, seed_to_value_map):
    matchup_key = f"{team1_seed}-{team2_seed}"
    cutoff_prob = seed_to_value_map.get(matchup_key, 0.5)  # Default probability is 0.5 if matchup key not found
    random_number = random.random()
    if random_number > cutoff_prob:
        return team1_seed
    else:
        return team2_seed

# Function to get team name from seed
def get_team_name(seed, region):
    if region == "West":
        return west_seed_to_team_map.get(seed, f"Team {seed}")
    elif region == "East":
        return east_seed_to_team_map.get(seed, f"Team {seed}")
    elif region == "Midwest":
        return midwest_seed_to_team_map.get(seed, f"Team {seed}")
    elif region == "South":
        return south_seed_to_team_map.get(seed, f"Team {seed}")

def region_winner(region_name):
    # Define the initial matchups for the first round
    matchups = ['1-16', '8-9', '5-12', '4-13', '6-11', '3-14', '7-10', '2-15']

    # Iterate through each round of matchups until there's only one matchup left
    while len(matchups) > 1:
        next_round_winners = []
        for i in range(0, len(matchups), 2):  # Iterate through matchups pairwise
            team1_seed, team2_seed = map(int, matchups[i].split('-'))
            winner1_seed = simulate_matchup(team1_seed, team2_seed, key_value_pairs)
            
            team1_seed, team2_seed = map(int, matchups[i+1].split('-'))
            winner2_seed = simulate_matchup(team1_seed, team2_seed, key_value_pairs)
            
            # Create a new matchup key based on the winners of the previous matchups
            new_matchup = f"{winner1_seed}-{winner2_seed}"
            next_round_winners.append(new_matchup)
        matchups = next_round_winners

    # Calculate the winner of the final matchup
    final_winner_seed = int(matchups[0].split('-')[0])
    return final_winner_seed

# Function to run multiple simulations and count the results
def run_simulations(num_simulations):
    results = {'Midwest': {i: 0 for i in range(1, 17)},
               'South': {i: 0 for i in range(1, 17)},
               'East': {i: 0 for i in range(1, 17)},
               'West': {i: 0 for i in range(1, 17)},
               'Winner_1': {get_team_name(i, "Winner_1"): 0 for i in range(1, 17)},
               'Winner_2': {get_team_name(i, "Winner_2"): 0 for i in range(1, 17)},
               'Final_Winner': {get_team_name(i, "Final_Winner"): 0 for i in range(1, 17)}}

    for _ in range(num_simulations):
        # Run the tournament
        midwest = region_winner("Midwest")
        south = region_winner("South")
        east = region_winner("East")
        west = region_winner("West")

        winner_1_seed = simulate_matchup(midwest, south, key_value_pairs)
        winner_2_seed = simulate_matchup(east, west, key_value_pairs)

        # Determine the winner between the winners of Region 2, Region 3, and Midwest (Region 1)
        final_winner_seed = simulate_matchup(winner_1_seed, winner_2_seed, key_value_pairs)

        # Increment the count for the final winner
        results['Midwest'][midwest] += 1
        results['South'][south] += 1
        results['East'][east] += 1
        results['West'][west] += 1
        results['Winner_1'][get_team_name(winner_1_seed, "Winner_1")] += 1
        results['Winner_2'][get_team_name(winner_2_seed, "Winner_2")] += 1
        results['Final_Winner'][get_team_name(final_winner_seed, "Final_Winner")] += 1

    return results
    
# Run 100 simulations
simulations_results = run_simulations(100)

# Print the results
for region, seeds in simulations_results.items():
    print(f"{region} wins:")
    for seed, count in seeds.items():
        team_name = get_team_name(seed, region)
        print(f"{team_name}: {count} times")
    print()
