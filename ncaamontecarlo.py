import pandas as pd
import random
import time
import os

# Define teams for each region with their corresponding winning probabilities
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

# Define the seed to region mapping
seed_to_region = {}
for region, teams_list in zip(['South', 'West', 'East', 'Midwest'], [south_teams_list, west_teams_list, east_teams_list, midwest_teams_list]):
    for seed, _, _ in teams_list:
        seed_to_region[seed] = region

# Define the matchups for each round
matchups_round_2 = [
    ('1-16', '8-9'),
    ('5-12', '4-13'),
    ('6-11', '3-14'),
    ('7-10', '2-15')
]

matchups_round_3 = [
    (None, None),  # Placeholder for winners of round 2 matchups
    (None, None)
]

matchups_round_4 = (None, None)  # Placeholder for winners of round 3 matchups

# Define the matchups for the final round
final_matchups = (None, None)

# Function to generate a random number between 0 and 1
def generate_random_number():
    # Combine system-provided randomness with random module
    random.seed(time.time() + os.getpid())
    # Generate a random number between 0 and 1
    random_number = random.uniform(0, 1)
    # Format the random number to match the specified format
    formatted_random_number = "{:.9f}".format(random_number)
    return formatted_random_number

# Function to get team name based on seed and region
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
    # Check if any seed is None
    if team1_seed is None:
        return team2_seed
    elif team2_seed is None:
        return team1_seed

    # Determine the higher and lower seeds
    higher_seed = max(team1_seed, team2_seed)
    lower_seed = min(team1_seed, team2_seed)
    
    # Retrieve the cutoff probability for the lower seed
    cutoff_prob = key_value_pairs[(seed_to_region[team1_seed], lower_seed)]
    # Generate a random number
    random_number = generate_random_number()
    
    # Compare the random number with the cutoff probability
    if float(random_number) < cutoff_prob:  # Corrected the comparison here
        return lower_seed
    else:
        return higher_seed

def run_simulations(num_simulations):
    results = {'Midwest': {i: 0 for i in range(1, 17)},
               'South': {i: 0 for i in range(1, 17)},
               'East': {i: 0 for i in range(1, 17)},
               'West': {i: 0 for i in range(1, 17)}}

    final_winner = {'region': None, 'seed': None}

    for _ in range(num_simulations):
        # Run round 2 matchups
        round_2_winners = []
        print("Round 2 winners:")
        for matchup in matchups_round_2:
            team1_seed, team2_seed = map(int, matchup[0].split('-'))
            winner1_seed = simulate_matchup(team1_seed, team2_seed, seeds)
            
            team1_seed, team2_seed = map(int, matchup[1].split('-'))
            winner2_seed = simulate_matchup(team1_seed, team2_seed, seeds)
            
            print(f"Matchup 1: {get_team_name(winner1_seed, seed_to_region[team1_seed])} vs. {get_team_name(winner2_seed, seed_to_region[team2_seed])}")
            round_2_winners.append((winner1_seed, winner2_seed))

        # Run round 3 matchups
        round_3_winners = []
        print("Round 3 winners:")
        for i, matchup in enumerate(matchups_round_3):
            if None in matchup:
                team1_seed, team2_seed = round_2_winners[i]
                winner1_seed = simulate_matchup(team1_seed, team2_seed, seeds)
                
                team1_seed, team2_seed = round_2_winners[i + 1]
                winner2_seed = simulate_matchup(team1_seed, team2_seed, seeds)
                
                print(f"Matchup {i + 1}: {get_team_name(winner1_seed, seed_to_region[team1_seed])} vs. {get_team_name(winner2_seed, seed_to_region[team2_seed])}")
                round_3_winners.append((winner1_seed, winner2_seed))
            else:
                round_3_winners.append(matchup)

        # Run round 4 matchups
        winner_1_seed, winner_2_seed = matchups_round_4
        if winner_1_seed is not None and winner_2_seed is not None:
            final_winner_seed = simulate_matchup(winner_1_seed, winner_2_seed, seeds)
            print("Round 4 winner:")
            print(f"{get_team_name(final_winner_seed, seed_to_region[winner_1_seed])} vs. {get_team_name(final_winner_seed, seed_to_region[winner_2_seed])}")

            # Determine the region and seed of the winner
            if final_winner_seed is not None:
                final_winner_region = seed_to_region[final_winner_seed]
                final_winner['region'] = final_winner_region
                final_winner['seed'] = final_winner_seed

            # Increment the count for the region winner and final winner
            if final_winner_seed is not None:
                results[final_winner['region']][final_winner['seed']] += 1

    return results, final_winner

# Run 100 simulations
simulations_results, final_winner = run_simulations(100)

# Print the results
for region, seeds in simulations_results.items():
    print(f"{region} wins:")
    for seed, count in seeds.items():
        team_name = get_team_name(seed, region)
        print(f"{team_name}: {count} times")
    print()

print(f"Final Winner is from {final_winner['region']}: {get_team_name(final_winner['seed'], final_winner['region'])}")
