import pandas as pd
import random
import time
import os


south_teams_list = [
    (1, 'Houston', 0.796178344),
    (2, 'Marquette', 0.706586826),
    (3, 'Kentucky', 0.655011655),
    (4, 'Duke', 0.61038961),
    (5, 'Wisconsin', 0.536585366),
    (6, 'Texas Tech', 0.514469453),
    (7, 'Florida', 0.421455939),
    (8, 'Nebraska', 0.421455939),
    (9, 'Texas A&M', 0.379591837),
    (10, 'Colorado', 0.379591837),
    (11, 'NC State', 0.392),
    (12, 'James Madison', 0.336244541),
    (13, 'Vermont', 0.2),
    (14, 'Oakland', 0.136363636),
    (15, 'Western Kentucky', 0.095238095),
    (16, 'Longwood', 0.012987013)
]

west_teams_list = [
    (1, 'North Carolina', 0.796178344),
    (2, 'Arizona', 0.706586826),
    (3, 'Baylor', 0.655011655),
    (4, 'Alabama', 0.61038961),
    (5, "Saint Mary's", 0.536585366),
    (6, 'Clemson', 0.514469453),
    (7, 'Dayton', 0.421455939),
    (8, 'Mississippi State', 0.421455939),
    (9, 'Michigan State', 0.379591837),
    (10, 'Nevada', 0.379591837),
    (11, 'New Mexico', 0.392),
    (12, 'Grand Canyon', 0.336244541),
    (13, 'Charleston', 0.2),
    (14, 'Colgate', 0.136363636),
    (15, 'Long Beach State', 0.095238095),
    (16, 'Wagner', 0.012987013)
]

east_teams_list = [
    (1, 'UConn', 0.796178344),
    (2, 'Iowa State', 0.706586826),
    (3, 'Illinois', 0.655011655),
    (4, 'Auburn', 0.61038961),
    (5, 'San Diego State', 0.536585366),
    (6, 'BYU', 0.514469453),
    (7, 'Washington State', 0.421455939),
    (8, 'Florida Atlantic', 0.421455939),
    (9, 'Northwestern', 0.379591837),
    (10, 'Drake', 0.379591837),
    (11, 'Duquesne', 0.392),
    (12, 'UAB', 0.336244541),
    (13, 'Yale', 0.2),
    (14, 'Morehead State', 0.136363636),
    (15, 'South Dakota State', 0.095238095),
    (16, 'Stetson', 0.012987013)
]

midwest_teams_list = [
    (1, 'Purdue', 0.796178344),
    (2, 'Tennessee', 0.706586826),
    (3, 'Creighton', 0.655011655),
    (4, 'Kansas', 0.61038961),
    (5, 'Gonzaga', 0.536585366),
    (6, 'South Carolina', 0.514469453),
    (7, 'Texas', 0.421455939),
    (8, 'Utah State', 0.421455939),
    (9, 'TCU', 0.379591837),
    (10, 'Colorado State', 0.379591837),
    (11, 'Oregon', 0.392),
    (12, 'McNeese', 0.336244541),
    (13, 'Samford', 0.2),
    (14, 'Akron', 0.136363636),
    (15, 'Saint Peter\'s', 0.095238095),
    (16, 'Grambling State', 0.012987013)
]

# Convert lists to dictionaries for easy lookup
south_teams = {team[0]: team[2] for team in south_teams_list}
west_teams = {team[0]: team[2] for team in west_teams_list}
east_teams = {team[0]: team[2] for team in east_teams_list}
midwest_teams = {team[0]: team[2] for team in midwest_teams_list}

# Define the seeds dictionary
seeds = {}
for region, teams_list in zip(['South', 'West', 'East', 'Midwest'], [south_teams_list, west_teams_list, east_teams_list, midwest_teams_list]):
    for seed, _, prob in teams_list:
        seeds[(region, seed)] = prob

def generate_random_number():
    # Combine system-provided randomness with random module
    random.seed(time.time() + os.getpid())
    # Generate a random number between 0 and 1
    random_number = random.uniform(0, 1)
    # Format the random number to match the specified format
    formatted_random_number = "{:.9f}".format(random_number)
    return formatted_random_number

def get_team_name(seed, region):
    if region == "West":
        return west_teams_list[seed-1][1]
    elif region == "East":
        return east_teams_list[seed-1][1]
    elif region == "Midwest":
        return midwest_teams_list[seed-1][1]
    elif region == "South":
        return south_teams_list[seed-1][1]

def simulate_matchup(team1_seed, team2_seed, key_value_pairs):
    # Determine the higher and lower seeds
    higher_seed = max(team1_seed, team2_seed)
    lower_seed = min(team1_seed, team2_seed)
    
    # Retrieve the cutoff probability for the lower seed
    cutoff_prob = key_value_pairs[(region, lower_seed)]
    # Generate a random number
    random_number = generate_random_number()
    
    # Invert the probability
    inverted_prob = 1 - cutoff_prob
    
    # Compare the random number with the inverted probability
    if float(random_number) > inverted_prob:
        return lower_seed
    else:
        return higher_seed

def region_winner(region_name):
    # Define the initial matchups for the first round
    matchups = ['1-16', '8-9', '5-12', '4-13', '6-11', '3-14', '7-10', '2-15']

    # Iterate through each round of matchups until there's only one matchup left
    while len(matchups) > 1:
        next_round_winners = []
        for i in range(0, len(matchups), 2):  # Iterate through matchups pairwise
            team1_seed, team2_seed = map(int, matchups[i].split('-'))
            winner1_seed = simulate_matchup(team1_seed, team2_seed, seeds)
            
            team1_seed, team2_seed = map(int, matchups[i+1].split('-'))
            winner2_seed = simulate_matchup(team1_seed, team2_seed, seeds)
            
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

        winner_1_seed = simulate_matchup(midwest, south, seeds)
        winner_2_seed = simulate_matchup(east, west, seeds)

        # Determine the winner between the winners of Region 2, Region 3, and Midwest (Region 1)
        final_winner_seed = simulate_matchup(winner_1_seed, winner_2_seed, seeds)

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
