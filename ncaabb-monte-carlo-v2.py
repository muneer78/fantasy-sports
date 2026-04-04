import csv
import random
from collections import Counter

year = "2026"

# Load team stats from 2026-ncaa.csv and compute composite score
team_scores = {}

# Load attendance data
attendance = {}
with open("ncaa_attendance.csv", mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        attendance[row["School"].strip()] = int(row["Attendance"])

with open(f"{year}-ncaa.csv", mode="r") as file:
    reader = csv.DictReader(file)
    all_three_pct = []
    all_orb = []
    all_att = []
    teams_data = []
    for row in reader:
        school = row["School"].strip()
        try:
            three_pct = float(row["3P%"])
            orb = float(row["ORB"])
        except (ValueError, KeyError):
            continue
        # Fuzzy match attendance
        att = attendance.get(school)
        if att is None:
            for key in attendance:
                if school.lower() in key.lower() or key.lower() in school.lower():
                    att = attendance[key]
                    break
        if att is None:
            att = 0
        teams_data.append((school, three_pct, orb, att))
        all_three_pct.append(three_pct)
        all_orb.append(orb)
        if att > 0:
            all_att.append(att)

    # Normalize 3P% and ORB to 0-1 range; attendance normalized only among schools that have it
    min_3p, max_3p = min(all_three_pct), max(all_three_pct)
    min_orb, max_orb = min(all_orb), max(all_orb)
    min_att, max_att = (min(all_att), max(all_att)) if all_att else (0, 1)

    for school, three_pct, orb, att in teams_data:
        norm_3p = (three_pct - min_3p) / (max_3p - min_3p) if max_3p != min_3p else 0.5
        norm_orb = (orb - min_orb) / (max_orb - min_orb) if max_orb != min_orb else 0.5
        norm_att = (att - min_att) / (max_att - min_att) if att > 0 and max_att != min_att else 0
        team_scores[school] = norm_3p + norm_orb + norm_att

# Load bracket matchups
bracket_teams = []
with open(f"{year}-bracket.csv", mode="r") as file:
    reader = csv.reader(file)
    for line in reader:
        bracket_teams.append(line)


unmatched_teams = set()

# Alias map: bracket name -> stats CSV name
name_aliases = {
    "BYU": "Brigham Young",
    "UConn": "Connecticut",
    "VCU": "Virginia Commonwealth",
    "UCSD": "UC San Diego",
    "St John's": "St. John's (NY)",
    "St Mary's": "Saint Mary's (CA)",
}

def get_score(team_name):
    """Look up composite score; fuzzy match if exact name not found."""
    name = team_name.strip()
    if name in team_scores:
        return team_scores[name]
    # Check aliases
    if name in name_aliases and name_aliases[name] in team_scores:
        return team_scores[name_aliases[name]]
    # Try partial match
    for key in team_scores:
        if name.lower() in key.lower() or key.lower() in name.lower():
            return team_scores[key]
    unmatched_teams.add(name)
    return 0.5  # default middle score if not found


def simulate_round(teams):
    """Simulate a round; higher composite score = higher win probability."""
    next_round = []
    winners = []
    for i in range(0, len(teams), 2):
        score_a = get_score(teams[i][0])
        score_b = get_score(teams[i + 1][0])
        total = score_a + score_b
        prob_a = score_a / total if total > 0 else 0.5
        if random.random() < prob_a:
            next_round.append(teams[i])
            winners.append(teams[i][0])
        else:
            next_round.append(teams[i + 1])
            winners.append(teams[i + 1][0])
    return next_round, winners


# Store winners for each round across simulations
round_winners = {r: [] for r in range(1, 7)}

num_simulations = 1000

for _ in range(num_simulations):
    teams = bracket_teams[:]
    for round_num in range(1, 7):
        if len(teams) <= 1:
            break
        teams, winners = simulate_round(teams)
        round_winners[round_num].extend(winners)

# Write results
round_labels = {1: "64", 2: "32", 3: "16", 4: "8", 5: "4", 6: "Championship"}
with open(f"{year}_montecarlo_v2_results.txt", "w") as f:
    for round_num, winners in round_winners.items():
        label = round_labels.get(round_num, "?")
        print(f"Round of {label}:", file=f)
        for i, (winner, count) in enumerate(Counter(winners).most_common()):
            print(f"  {winner}: {count}/{num_simulations} sims ({count*100//num_simulations}%)", file=f)
        print(file=f)

print(f"Simulation complete. Results written to {year}_montecarlo_v2_results.txt")

if unmatched_teams:
    print(f"\nWARNING: {len(unmatched_teams)} bracket team(s) not matched in {year}-ncaa.csv:")
    for team in sorted(unmatched_teams):
        print(f"  - {team}")
else:
    print("\nAll bracket teams matched successfully.")
