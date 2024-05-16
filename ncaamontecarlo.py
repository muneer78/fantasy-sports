from tqdm import tqdm
import random

# Define the seeds dictionary
seeds = {
    1: 0.796178344,
    2: 0.706586826,
    3: 0.655011655,
    4: 0.61038961,
    5: 0.536585366,
    6: 0.514469453,
    7: 0.421455939,
    8: 0.421455939,
    9: 0.379591837,
    10: 0.379591837,
    11: 0.392,
    12: 0.336244541,
    13: 0.2,
    14: 0.136363636,
    15: 0.095238095,
    16: 0.012987013
}

# Define the teams dictionaries
south_teams_dict = {
    1: ('Houston', 0.796178344),
    2: ('Marquette', 0.706586826),
    3: ('Kentucky', 0.655011655),
    4: ('Duke', 0.61038961),
    5: ('Wisconsin', 0.536585366),
    6: ('Texas Tech', 0.514469453),
    7: ('Florida', 0.421455939),
    8: ('Nebraska', 0.421455939),
    9: ('Texas A&M', 0.379591837),
    10: ('Colorado', 0.379591837),
    11: ('NC State', 0.392),
    12: ('James Madison', 0.336244541),
    13: ('Vermont', 0.2),
    14: ('Oakland', 0.136363636),
    15: ('Western Kentucky', 0.095238095),
    16: ('Longwood', 0.012987013)
}

west_teams_dict = {
    1: ('North Carolina', 0.796178344),
    2: ('Arizona', 0.706586826),
    3: ('Baylor', 0.655011655),
    4: ('Alabama', 0.61038961),
    5: ("Saint Mary's", 0.536585366),
    6: ('Clemson', 0.514469453),
    7: ('Dayton', 0.421455939),
    8: ('Mississippi State', 0.421455939),
    9: ('Michigan State', 0.379591837),
    10: ('Nevada', 0.379591837),
    11: ('New Mexico', 0.392),
    12: ('Grand Canyon', 0.336244541),
    13: ('Charleston', 0.2),
    14: ('Colgate', 0.136363636),
    15: ('Long Beach State', 0.095238095),
    16: ('Wagner', 0.012987013)
}

east_teams_dict = {
    1: ('UConn', 0.796178344),
    2: ('Iowa State', 0.706586826),
    3: ('Illinois', 0.655011655),
    4: ('Auburn', 0.61038961),
    5: ('San Diego State', 0.536585366),
    6: ('BYU', 0.514469453),
    7: ('Washington State', 0.421455939),
    8: ('Florida Atlantic', 0.421455939),
    9: ('Northwestern', 0.379591837),
    10: ('Drake', 0.379591837),
    11: ('Duquesne', 0.392),
    12: ('UAB', 0.336244541),
    13: ('Yale', 0.2),
    14: ('Morehead State', 0.136363636),
    15: ('South Dakota State', 0.095238095),
    16: ('Stetson', 0.012987013)
}

midwest_teams_dict = {
    1: ('Purdue', 0.796178344),
    2: ('Tennessee', 0.706586826),
    3: ('Creighton', 0.655011655),
    4: ('Kansas', 0.61038961),
    5: ('Gonzaga', 0.536585366),
    6: ('South Carolina', 0.514469453),
    7: ('Texas', 0.421455939),
    8: ('Utah State', 0.421455939),
    9: ('TCU', 0.379591837),
    10: ('Colorado State', 0.379591837),
    11: ('Oregon', 0.392),
    12: ('McNeese', 0.336244541),
    13: ('Samford', 0.2),
    14: ('Akron', 0.136363636),
    15: ('Saint Peter\'s', 0.095238095),
    16: ('Grambling State', 0.012987013)
}

def generate_random_seed():
    return random.random()

def generator(teams_dict, seeds):
    winning_probs = [seeds[seed] for seed in seeds]
    teams = [team[0] for team in teams_dict.values()]
    bracket = []
    matchups = [(teams[i], teams[15 - i]) for i in range(16)]
    for matchup in matchups:
        team1, team2 = matchup
        if random.random() < winning_probs[teams.index(team1)]:
            bracket.append(team1)
        else:
            bracket.append(team2)
    return bracket
    

def simulate_tournament(teams_dict, seeds, n_simulations=100):
    results = []
    for _ in tqdm(range(n_simulations)):
        # Simulate tournaments for each region
        south_results = simulate_region(south_teams_dict, seeds)
        west_results = simulate_region(west_teams_dict, seeds)
        east_results = simulate_region(east_teams_dict, seeds)
        midwest_results = simulate_region(midwest_teams_dict, seeds)

        # Simulate the Final Four
        south_winner = random.choice(south_results)
        west_winner = random.choice(west_results)
        east_winner = random.choice(east_results)
        midwest_winner = random.choice(midwest_results)

        # Determine which regions face off in the championship
        final_four_matchup_1 = [midwest_winner, south_winner]
        final_four_matchup_2 = [west_winner, east_winner]

        # Simulate the Championship game
        if seeds[1] + seeds[2] > seeds[3] + seeds[4]:
            championship_game = [final_four_matchup_1[0], final_four_matchup_2[1]]
        else:
            championship_game = [final_four_matchup_1[1], final_four_matchup_2[0]]

        results.append(championship_game)
    return results

def simulate_region(teams_dict, seeds):
    results = []
    for _ in range(100):
        bracket = generator(teams_dict, seeds)
        results.append(bracket)
    return results

# Simulate tournaments for each region
south_results = simulate_tournament(south_teams_dict, seeds)
west_results = simulate_tournament(west_teams_dict, seeds)
east_results = simulate_tournament(east_teams_dict, seeds)
midwest_results = simulate_tournament(midwest_teams_dict, seeds)

# Function to count occurrences of each team in the results
def count_occurrences(results):
    counts = {}
    for bracket in results:
        for game in bracket:
            for team in game:
                if team in counts:
                    counts[team] += 1
                else:
                    counts[team] = 1
    return counts

# Count occurrences for each region
south_counts = count_occurrences(south_results)
west_counts = count_occurrences(west_results)
east_counts = count_occurrences(east_results)
midwest_counts = count_occurrences(midwest_results)

# Function to sort the counts and extract the top 3 teams
def get_top_teams_with_counts(counts, n=3):
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_teams = sorted_counts[:n]
    return top_teams

# Get the top 3 teams with counts from each region
top_south_teams_with_counts = get_top_teams_with_counts(south_counts)
top_west_teams_with_counts = get_top_teams_with_counts(west_counts)
top_east_teams_with_counts = get_top_teams_with_counts(east_counts)
top_midwest_teams_with_counts = get_top_teams_with_counts(midwest_counts)

# Simulate tournaments for each region and championship
championship_results = simulate_tournament(south_teams_dict, seeds)

# Count occurrences for the championship
championship_counts = count_occurrences(championship_results)

# Print the top 3 teams from each region
print("Top 3 Teams from South Region:")
for i, (team, _) in enumerate(top_south_teams_with_counts, start=1):
    print(f"{i}. {team}")

print("\nTop 3 Teams from West Region:")
for i, (team, _) in enumerate(top_west_teams_with_counts, start=1):
    print(f"{i}. {team}")

print("\nTop 3 Teams from East Region:")
for i, (team, _) in enumerate(top_east_teams_with_counts, start=1):
    print(f"{i}. {team}")

print("\nTop 3 Teams from Midwest Region:")
for i, (team, _) in enumerate(top_midwest_teams_with_counts, start=1):
    print(f"{i}. {team}")

# Print the number of times each team wins the championship
print("Championship Wins:")
sorted_championship_counts = sorted(championship_counts.items(), key=lambda x: x[1], reverse=True)
for team, count in sorted_championship_counts:
    print(f"{team}: {count}")
