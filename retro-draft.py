# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "polars>=1.0",
#     "polars-baseball @ git+https://github.com/nicko4o/polars-baseball.git@b221441ae4b0dd9aa36aba82611b771f671d3255",
#     "textual>=8.2.8",
# ]
# ///

import argparse
import asyncio
from collections import Counter
from datetime import date
import random
from pathlib import Path

import polars as pl
import polars_baseball as pb


VERSION = "3.0.0"
ROSTER_SLOTS = (
    "C", "1B", "2B", "SS", "3B",
    "OF", "OF", "OF", "UTIL",
    "SP", "SP", "SP", "RP", "RP", "P", "P", "P",
    "BN", "BN", "BN", "BN",
)
HITTING_STATS = [
    "G_Bat", "PA", "AB", "R_Bat", "H_Bat", "2B", "3B", "HR_Bat",
    "RBI", "SB", "CS", "BB_Bat", "SO_Bat", "WAR_Bat",
]
PITCHING_STATS = [
    "W", "L", "G_Pitch", "GS", "SV", "IP", "H_Pitch", "ER",
    "BB_Pitch", "SO_Pitch", "WAR_Pitch",
]
ROTO_CATEGORIES = [
    ("AVG", True),
    ("R", True),
    ("HR", True),
    ("RBI", True),
    ("SB", True),
    ("W", True),
    ("SV", True),
    ("SO", True),
    ("ERA", False),
    ("WHIP", False),
]
PLAYER_STAT_COLUMNS = (
    "AVG", "R", "HR", "RBI", "SB", "W", "SV", "SO", "ERA", "WHIP", "WAR"
)


def value(players, player_id, column):
    return players.filter(pl.col("ID") == player_id).item(0, column)


async def fetch_table(year, kind, context):
    fetch = pb.fangraphs.batting if kind == "batting" else pb.fangraphs.pitching
    return await fetch(
        start_season=year,
        end_season=year,
        qual=0,
        max_results=5000,
        context=context,
    )


async def download_table(year, kind, data_dir, context, refresh=False):
    filename = data_dir / f"fangraphs-{year}-{kind}.csv"
    if filename.exists() and not refresh:
        table = pl.read_csv(filename, infer_schema_length=None)
        validate_table(table, kind)
        return table

    print(f"Fetching {year} FanGraphs {kind} data using polars-baseball...")
    try:
        table = await fetch_table(year, kind, context)
    except Exception as error:
        raise RuntimeError(f"FanGraphs {kind} download failed: {error}") from error

    if "playerid" in table.columns:
        table = table.rename({"playerid": "PlayerID"})
    validate_table(table, kind)
    data_dir.mkdir(parents=True, exist_ok=True)
    table.write_csv(filename)
    return table


def validate_table(table, kind):
    required = {"PlayerID", "Name", "Team", "WAR", "G"}
    required |= {"PA", "AB", "H"} if kind == "batting" else {"IP", "GS"}
    missing = required - set(table.columns)
    if table.is_empty() or missing:
        raise ValueError(f"Invalid FanGraphs {kind} data; missing columns: {sorted(missing)}")
    ids = table.get_column("PlayerID")
    if ids.null_count() or ids.n_unique() != table.height:
        raise ValueError(f"Expected one season-total row per FanGraphs player in {kind} data.")


def combine_tables(batters, pitchers):
    validate_table(batters, "batting")
    validate_table(pitchers, "pitching")
    tables = []
    for table, columns, suffix, extra in [
        (batters, HITTING_STATS, "_Bat", ["position"]),
        (pitchers, PITCHING_STATS, "_Pitch", []),
    ]:
        mapping = {column.removesuffix(suffix): column for column in columns}
        selected = [column for column in mapping if column in table.columns]
        tables.append(
            table.select("PlayerID", "Name", "Team", *extra, *selected).rename(
                {
                    **{column: mapping[column] for column in selected},
                    **({"position": "FieldPosition"} if extra else {}),
                }
            )
        )

    players = tables[0].join(
        tables[1], on="PlayerID", how="full", suffix="_Pitcher", coalesce=True
    )
    players = players.with_columns(
        pl.coalesce("Name", "Name_Pitcher").alias("Name"),
        pl.coalesce("Team", "Team_Pitcher").alias("Team"),
    ).drop("Name_Pitcher", "Team_Pitcher")
    players = players.with_columns(
        pl.col("WAR_Bat").cast(pl.Float64, strict=False).fill_null(0),
        pl.col("WAR_Pitch").cast(pl.Float64, strict=False).fill_null(0),
    ).with_columns(
        (pl.col("WAR_Bat") + pl.col("WAR_Pitch")).alias("Total_WAR")
    )
    return players.sort("Total_WAR", descending=True)


def download_season(year, data_dir, refresh=False):
    async def download():
        # curl_cffi resources must be created, used, and closed on one event loop.
        async with pb.BaseballContext() as context:
            batters = await download_table(
                year, "batting", data_dir, context, refresh
            )
            pitchers = await download_table(
                year, "pitching", data_dir, context, refresh
            )
            return batters, pitchers

    return combine_tables(*asyncio.run(download()))


def load_players(players, number_of_teams):
    required = {
        "Name", "Team", "FieldPosition", "PA", "IP", "G_Pitch", "GS",
        "Total_WAR",
    }
    missing = required - set(players.columns)
    if missing:
        raise ValueError(f"Downloaded data is missing: {', '.join(sorted(missing))}")

    numeric = [
        column
        for column in set(HITTING_STATS + PITCHING_STATS + ["Total_WAR"])
        if column in players.columns
    ]
    players = players.with_columns(
        pl.col(column).cast(pl.Float64, strict=False).fill_null(0)
        for column in numeric
    )
    is_pitcher = (pl.col("IP") > 0) & (pl.col("IP") * 3 >= pl.col("PA"))
    players = (
        players.filter(pl.col("Name").is_not_null() & (pl.col("Name") != "Player"))
        .with_columns(pl.col("Name").str.replace(r"[*#]+$", ""))
        .with_columns(
            pl.when(is_pitcher)
            .then(
                pl.when(pl.col("GS") >= pl.col("G_Pitch") / 2)
                .then(pl.lit("SP"))
                .otherwise(pl.lit("RP"))
            )
            .otherwise(pl.lit("H"))
            .alias("Position"),
            pl.when(is_pitcher)
            .then(pl.lit("P"))
            .otherwise(pl.lit("H"))
            .alias("Type"),
            pl.col("Total_WAR").alias("WAR"),
        )
        .with_row_index("ID", offset=1)
    )
    players = players.with_columns(
        pl.when(pl.col("Type") == "H")
        .then(
            pl.col("FieldPosition")
            .fill_null("UTIL")
            .str.to_uppercase()
            .str.replace_all(r"[^A-Z0-9/]", "")
        )
        .otherwise(pl.col("Position"))
        .alias("Position")
    )

    requirements = {
        "C": 1, "1B": 1, "2B": 1, "SS": 1, "3B": 1, "OF": 3,
        "SP": 3, "RP": 2,
    }
    for position, per_team in requirements.items():
        if position in {"SP", "RP"}:
            found = players.filter(pl.col("Position") == position).height
        else:
            found = players.filter(
                (pl.col("Type") == "H")
                & pl.col("Position").str.split("/").list.contains(position)
            ).height
        needed = per_team * number_of_teams
        if found < needed:
            raise ValueError(
                f"The draft needs {needed} {position}-eligible players, "
                f"but the data has {found}."
            )
    return players


def roster_count(roster, players, kind):
    return players.filter(
        pl.col("ID").is_in(roster) & (pl.col("Type") == kind)
    ).height


def eligible_for_slot(player, slot):
    if slot == "BN":
        return True
    if slot == "UTIL":
        return player["Type"] == "H"
    if slot == "P":
        return player["Type"] == "P"
    if slot in {"SP", "RP"}:
        return player["Position"] == slot
    return (
        player["Type"] == "H"
        and slot in player["Position"].split("/")
    )


def assign_roster(roster, players):
    if len(roster) > len(ROSTER_SLOTS):
        return None
    records = {
        row["ID"]: row
        for row in players.filter(pl.col("ID").is_in(roster))
        .select("ID", "Type", "Position")
        .iter_rows(named=True)
    }
    if len(records) != len(roster):
        return None

    active_slots = [
        (index, slot)
        for index, slot in enumerate(ROSTER_SLOTS)
        if slot != "BN"
    ]
    slots = (
        list(enumerate(ROSTER_SLOTS))
        if len(roster) > len(active_slots)
        else active_slots
    )
    slot_order = {"BN": 2, "UTIL": 1, "P": 1}
    choices = {
        player_id: [
            index
            for index, slot in sorted(
                slots, key=lambda item: slot_order.get(item[1], 0)
            )
            if eligible_for_slot(records[player_id], slot)
        ]
        for player_id in roster
    }
    matched = {}

    def place(player_id, seen):
        for slot_index in choices[player_id]:
            if slot_index in seen:
                continue
            seen.add(slot_index)
            if slot_index not in matched or place(matched[slot_index], seen):
                matched[slot_index] = player_id
                return True
        return False

    for player_id in sorted(roster, key=lambda item: len(choices[item])):
        if not place(player_id, set()):
            return None
    return {
        player_id: ROSTER_SLOTS[slot_index]
        for slot_index, player_id in matched.items()
    }


def roster_needs(roster, players):
    assignment = assign_roster(roster, players) or {}
    filled = list(assignment.values())
    needs = []
    for slot in ROSTER_SLOTS:
        if slot in filled:
            filled.remove(slot)
        else:
            needs.append(slot)
    return needs


def format_roster_needs(roster, players):
    counts = Counter(roster_needs(roster, players))
    return ", ".join(
        f"{count} {slot}" for slot, count in counts.items()
    ) or "complete"


def valid_pick(player_id, roster, players):
    return assign_roster([*roster, player_id], players) is not None


def computer_pick(roster, available, players, rng):
    choices = players.filter(pl.col("ID").is_in(available)).sort(
        "WAR", descending=True
    )
    for war_group in choices.partition_by("WAR", maintain_order=True):
        valid_ids = [
            player_id
            for player_id in war_group.get_column("ID")
            if valid_pick(player_id, roster, players)
        ]
        if valid_ids:
            return rng.choice(valid_ids)
    raise RuntimeError("No available player can complete this roster.")


def innings_to_outs(innings):
    if innings is None:
        return 0
    whole, _, fraction = str(innings).partition(".")
    return int(float(whole or 0)) * 3 + int((fraction or "0")[0])


def player_stat_cells(player):
    if player["Type"] == "H":
        average = player["H_Bat"] / player["AB"] if player["AB"] else None
        values = [
            f"{average:.3f}" if average is not None else "—",
            f"{player['R_Bat']:.0f}",
            f"{player['HR_Bat']:.0f}",
            f"{player['RBI']:.0f}",
            f"{player['SB']:.0f}",
            "—", "—", "—", "—", "—",
        ]
    else:
        innings = innings_to_outs(player["IP"]) / 3
        era = player["ER"] * 9 / innings if innings else None
        whip = (
            (player["BB_Pitch"] + player["H_Pitch"]) / innings
            if innings
            else None
        )
        values = [
            "—", "—", "—", "—", "—",
            f"{player['W']:.0f}",
            f"{player['SV']:.0f}",
            f"{player['SO_Pitch']:.0f}",
            f"{era:.2f}" if era is not None else "—",
            f"{whip:.2f}" if whip is not None else "—",
        ]
    return [*values, f"{player['WAR']:.1f}"]


def roto_stats(roster, players):
    selected = players.filter(pl.col("ID").is_in(roster))

    def total(column):
        return selected.get_column(column).sum() or 0

    ab = total("AB")
    hits = total("H_Bat")
    outs = sum(innings_to_outs(item) for item in selected.get_column("IP"))
    innings = outs / 3
    return {
        "AVG": hits / ab if ab else None,
        "R": total("R_Bat"),
        "HR": total("HR_Bat"),
        "RBI": total("RBI"),
        "SB": total("SB"),
        "W": total("W"),
        "SV": total("SV"),
        "SO": total("SO_Pitch"),
        "ERA": total("ER") * 9 / innings if innings else None,
        "WHIP": (
            (total("BB_Pitch") + total("H_Pitch")) / innings
            if innings
            else None
        ),
    }


def roto_standings(teams, players):
    rows = [{"Team": team, **roto_stats(roster, players)} for team, roster in teams.items()]
    points = {team: {} for team in teams}
    team_count = len(teams)

    for category, higher_is_better in ROTO_CATEGORIES:
        # Teams without a denominator for a rate category rank last.
        ordered = sorted(
            rows,
            key=lambda row: (
                row[category] is not None,
                row[category] if higher_is_better else -row[category]
                if row[category] is not None
                else float("-inf"),
            ),
        )
        index = 0
        while index < team_count:
            end = index + 1
            while end < team_count and ordered[end][category] == ordered[index][category]:
                end += 1
            tied_points = sum(range(index + 1, end + 1)) / (end - index)
            for row in ordered[index:end]:
                points[row["Team"]][category] = tied_points
            index = end

    for row in rows:
        team = row["Team"]
        for category, _ in ROTO_CATEGORIES:
            row[f"{category}_Pts"] = points[team][category]
        row["Roto_Pts"] = sum(points[team].values())
    return sorted(rows, key=lambda row: row["Roto_Pts"], reverse=True)


def stat_totals(roster, players, kind, columns):
    stats = [column for column in columns if column in players.columns]
    if not roster:
        return {column: 0 for column in stats}
    selected = players.filter(pl.col("ID").is_in(roster))
    totals = {
        column: round(selected.get_column(column).sum(), 3) for column in stats
    }
    if "IP" in stats:
        outs = sum(innings_to_outs(item) for item in selected.get_column("IP"))
        totals["IP"] = f"{outs // 3}.{outs % 3}"
    return totals


def show_other_teams(
    teams, user_team, players, title="Other teams before your pick:"
):
    print(f"\n{title}")
    summaries = []
    for team, roster in teams.items():
        if team == user_team:
            continue
        selected = players.filter(pl.col("ID").is_in(roster))
        hitting = stat_totals(roster, players, "H", HITTING_STATS)
        pitching = stat_totals(roster, players, "P", PITCHING_STATS)
        summaries.append(
            {
                "Team": team,
                "H": roster_count(roster, players, "H"),
                "P": roster_count(roster, players, "P"),
                "Total_fWAR": (
                    round(selected.get_column("WAR").sum(), 3) if roster else 0
                ),
                **{
                    f"H_{stat.removesuffix('_Bat')}": result
                    for stat, result in hitting.items()
                },
                **{
                    f"P_{stat.removesuffix('_Pitch')}": result
                    for stat, result in pitching.items()
                },
            }
        )

    if summaries:
        with pl.Config(tbl_rows=-1, tbl_cols=-1, tbl_width_chars=240):
            print(pl.DataFrame(summaries))
    for team, roster in teams.items():
        if team != user_team:
            names = [
                f"{value(players, player_id, 'Name')} "
                f"({value(players, player_id, 'Position')})"
                for player_id in roster
            ]
            print(f"{team}: {', '.join(names) or '-'}")


def show_available(available, players, show_all=False):
    columns = [
        column
        for column in ["ID", "Name", "Position", "Team", "WAR"]
        if column in players.columns
    ]
    choices = (
        players.filter(pl.col("ID").is_in(available))
        .select(columns)
        .sort("WAR", descending=True)
    )
    if not show_all:
        choices = choices.head(25)
    print("\nAvailable players (highest WAR first):")
    with pl.Config(tbl_rows=-1, tbl_cols=-1):
        print(choices)


def user_pick(roster, available, players):
    show_available(available, players)
    while True:
        answer = input("Pick a player ID ('all' shows everyone): ").strip().lower()
        if answer == "all":
            show_available(available, players, show_all=True)
            continue
        if not answer.isdigit() or int(answer) not in available:
            print("Enter an available player ID.")
            continue
        player_id = int(answer)
        if not valid_pick(player_id, roster, players):
            print("That player cannot fit your remaining required roster slots.")
            continue
        return player_id


def draft(players, number_of_teams, user_slot, seed=None):
    rng = random.Random(seed)
    team_names = [
        "You" if slot == user_slot else f"Team {slot}"
        for slot in range(1, number_of_teams + 1)
    ]
    teams = {team: [] for team in team_names}
    available = set(players.get_column("ID"))

    for round_number in range(1, len(ROSTER_SLOTS) + 1):
        order = team_names if round_number % 2 else reversed(team_names)
        for team in order:
            if team == "You":
                show_other_teams(teams, "You", players)
                print(
                    f"\nRound {round_number}, pick {user_slot}. "
                    f"You still need: {format_roster_needs(teams[team], players)}."
                )
                player_id = user_pick(teams[team], available, players)
            else:
                player_id = computer_pick(teams[team], available, players, rng)
            teams[team].append(player_id)
            available.remove(player_id)
            print(
                f"{team} drafted {value(players, player_id, 'Name')} "
                f"({value(players, player_id, 'Position')})."
            )
    return teams


def build_tui(players, number_of_teams, user_slot, seed=None):
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Horizontal
        from textual.widgets import DataTable, Footer, Header, Input, Static
    except ImportError as error:
        raise RuntimeError("Install the TUI dependencies with: uv sync") from error

    class DraftApp(App):
        TITLE = (
            f"{players.get_column('Season')[0]} Fantasy Baseball Draft"
            if "Season" in players.columns
            else "Fantasy Baseball Draft"
        )
        CSS = """
        Screen { layout: vertical; }
        #status { height: 3; padding: 0 1; color: $text-accent; }
        .tables { height: 1fr; }
        .panel { width: 1fr; border: solid $primary; }
        #pick { dock: bottom; margin: 0 1 1 1; }
        """
        BINDINGS = [("q", "quit", "Quit")]

        def __init__(self):
            super().__init__()
            self.rng = random.Random(seed)
            self.team_names = [
                "You" if slot == user_slot else f"Team {slot}"
                for slot in range(1, number_of_teams + 1)
            ]
            self.teams = {team: [] for team in self.team_names}
            self.available = set(players.get_column("ID"))
            self.picks = []
            self.order = [
                (round_number, team)
                for round_number in range(1, len(ROSTER_SLOTS) + 1)
                for team in (
                    self.team_names
                    if round_number % 2
                    else reversed(self.team_names)
                )
            ]
            self.cursor = 0

        def compose(self) -> ComposeResult:
            yield Header()
            yield Static(id="status")
            with Horizontal(classes="tables"):
                yield DataTable(id="standings", classes="panel")
                yield DataTable(id="board", classes="panel")
            with Horizontal(classes="tables"):
                yield DataTable(id="rosters", classes="panel")
                yield DataTable(id="available", classes="panel")
            yield Input(
                placeholder="Enter an available player ID and press Enter",
                id="pick",
                type="integer",
            )
            yield Footer()

        def on_mount(self):
            self.query_one("#standings", DataTable).add_columns(
                "Team", "AVG", "R", "HR", "RBI", "SB",
                "W", "SV", "SO", "ERA", "WHIP", "Pts",
            )
            self.query_one("#board", DataTable).add_columns(
                "Pick", "Rd", "Team", "Player", "Pos", *PLAYER_STAT_COLUMNS
            )
            self.query_one("#rosters", DataTable).add_columns(
                "Team", "Slot", "Player", "Pos", *PLAYER_STAT_COLUMNS
            )
            self.query_one("#available", DataTable).add_columns(
                "ID", "Player", "Pos", "Team", *PLAYER_STAT_COLUMNS
            )
            for table in self.query(DataTable):
                table.zebra_stripes = True
                table.cursor_type = "row"
            self.advance_computer_picks()

        def advance_computer_picks(self):
            while self.cursor < len(self.order):
                round_number, team = self.order[self.cursor]
                if team == "You":
                    break
                player_id = computer_pick(
                    self.teams[team], self.available, players, self.rng
                )
                self.record_pick(round_number, team, player_id)
            self.refresh_tables()

        def record_pick(self, round_number, team, player_id):
            self.teams[team].append(player_id)
            self.available.remove(player_id)
            self.picks.append(
                {
                    "Pick": self.cursor + 1,
                    "Round": round_number,
                    "Team": team,
                    "ID": player_id,
                }
            )
            self.cursor += 1

        def on_input_submitted(self, event: Input.Submitted):
            answer = event.value.strip()
            event.input.value = ""
            if self.cursor >= len(self.order):
                return
            if not answer.isdigit() or int(answer) not in self.available:
                self.notify("Enter an available player ID.", severity="error")
                return
            player_id = int(answer)
            if not valid_pick(player_id, self.teams["You"], players):
                self.notify(
                    "That player cannot fit your remaining roster slots.",
                    severity="error",
                )
                return
            round_number, team = self.order[self.cursor]
            self.record_pick(round_number, team, player_id)
            self.advance_computer_picks()

        def refresh_tables(self):
            self.refresh_standings()
            self.refresh_board()
            self.refresh_rosters()
            self.refresh_available()

            status = self.query_one("#status", Static)
            pick_input = self.query_one("#pick", Input)
            if self.cursor >= len(self.order):
                winner = roto_standings(self.teams, players)[0]
                status.update(
                    f"Draft complete — roto leader: {winner['Team']} "
                    f"({winner['Roto_Pts']:.1f} points)"
                )
                pick_input.disabled = True
                return
            round_number, _ = self.order[self.cursor]
            status.update(
                f"Round {round_number} • Overall pick {self.cursor + 1} • "
                f"Open slots: "
                f"{format_roster_needs(self.teams['You'], players)}"
            )
            pick_input.focus()

        def refresh_standings(self):
            table = self.query_one("#standings", DataTable)
            table.clear()
            for row in roto_standings(self.teams, players):
                rate = lambda category, digits: (
                    "—"
                    if row[category] is None
                    else f"{row[category]:.{digits}f}"
                )
                table.add_row(
                    row["Team"],
                    rate("AVG", 3),
                    f"{row['R']:.0f}",
                    f"{row['HR']:.0f}",
                    f"{row['RBI']:.0f}",
                    f"{row['SB']:.0f}",
                    f"{row['W']:.0f}",
                    f"{row['SV']:.0f}",
                    f"{row['SO']:.0f}",
                    rate("ERA", 2),
                    rate("WHIP", 2),
                    f"{row['Roto_Pts']:.1f}",
                )

        def refresh_board(self):
            table = self.query_one("#board", DataTable)
            table.clear()
            for pick in self.picks:
                player_id = pick["ID"]
                player = players.filter(pl.col("ID") == player_id).row(
                    0, named=True
                )
                table.add_row(
                    str(pick["Pick"]),
                    str(pick["Round"]),
                    pick["Team"],
                    player["Name"],
                    player["Position"],
                    *player_stat_cells(player),
                )
            if self.picks:
                table.move_cursor(row=table.row_count - 1)

        def refresh_rosters(self):
            table = self.query_one("#rosters", DataTable)
            table.clear()
            for team, roster in self.teams.items():
                assignment = assign_roster(roster, players) or {}
                for player_id in roster:
                    player = players.filter(pl.col("ID") == player_id).row(
                        0, named=True
                    )
                    table.add_row(
                        team,
                        assignment.get(player_id, "—"),
                        player["Name"],
                        player["Position"],
                        *player_stat_cells(player),
                    )

        def refresh_available(self):
            table = self.query_one("#available", DataTable)
            table.clear()
            choices = (
                players.filter(pl.col("ID").is_in(self.available))
                .sort("WAR", descending=True)
                .head(75)
            )
            for row in choices.iter_rows(named=True):
                table.add_row(
                    str(row["ID"]),
                    row["Name"],
                    row["Position"],
                    row["Team"],
                    *player_stat_cells(row),
                )

    return DraftApp()


def run_tui(players, number_of_teams, user_slot, seed=None):
    build_tui(players, number_of_teams, user_slot, seed).run()


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Historical fantasy draft using polars-baseball / FanGraphs (fWAR)."
        )
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Season to draft; prompts when omitted (default: 1992)",
    )
    parser.add_argument("--data-dir", type=Path, default=Path("baseball_data"))
    parser.add_argument("--refresh", action="store_true", help="Download the season again")
    parser.add_argument("--teams", type=int, default=10)
    parser.add_argument("--slot", type=int, help="Your draft position")
    parser.add_argument("--seed", type=int, help="Repeat the same random draft")
    parser.add_argument("--tui", action="store_true", help="Run the interactive draft board")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser.parse_args()


def choose_year(year):
    if year is None:
        answer = input("Choose a season [1992]: ").strip()
        year = int(answer) if answer else 1992
    if not 1871 <= year <= date.today().year:
        raise ValueError(f"Season must be between 1871 and {date.today().year}.")
    return year


def main():
    args = parse_args()
    if args.teams < 2:
        raise ValueError("There must be at least two teams.")
    year = choose_year(args.year)
    slot = (
        args.slot
        if args.slot is not None
        else int(input(f"Choose your draft position (1-{args.teams}): "))
    )
    if not 1 <= slot <= args.teams:
        raise ValueError(f"Draft position must be between 1 and {args.teams}.")

    players = load_players(
        download_season(year, args.data_dir, args.refresh), args.teams
    )
    if args.tui:
        run_tui(players, args.teams, slot, args.seed)
        return

    teams = draft(players, args.teams, slot, args.seed)
    print("\nFinal rosters:")
    show_other_teams(teams, "", players, title="All teams:")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(str(error)) from None
