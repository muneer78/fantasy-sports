import pandas as pd
import os


def convert_column_headers_to_lower_case(df):
    df.columns = [column.lower().strip() for column in df.columns]


def load_and_convert_data(file, expected_columns):
    """Load CSV and handle missing files or columns gracefully"""
    if not os.path.exists(file):
        print(f"Warning: File {file} not found. Skipping...")
        return None

    try:
        # First, read the file to see what columns are available
        df_peek = pd.read_csv(file, nrows=0)  # Just read headers
        available_columns = df_peek.columns.tolist()

        print(f"File: {file}")
        print(f"Available columns: {available_columns}")
        print(f"Expected columns: {expected_columns}")

        # Find which expected columns actually exist (case-insensitive)
        available_lower = [col.lower().strip() for col in available_columns]
        expected_lower = [col.lower().strip() for col in expected_columns]

        columns_to_use = []
        for expected in expected_columns:
            expected_clean = expected.lower().strip()
            # Try exact match first
            if expected_clean in available_lower:
                idx = available_lower.index(expected_clean)
                columns_to_use.append(available_columns[idx])
            # Try partial matching for common variations
            else:
                found = False
                for avail_col in available_columns:
                    avail_clean = avail_col.lower().strip()
                    # Check if the expected column name is contained in available column
                    if expected_clean in avail_clean or avail_clean in expected_clean:
                        columns_to_use.append(avail_col)
                        found = True
                        break

                if not found:
                    print(f"Warning: Column '{expected}' not found in {file}")

        if not columns_to_use:
            print(f"Warning: No matching columns found in {file}. Loading all columns.")
            df = pd.read_csv(file)
        else:
            print(f"Using columns: {columns_to_use}")
            df = pd.read_csv(file, usecols=columns_to_use)

        convert_column_headers_to_lower_case(df)
        return df

    except Exception as e:
        print(f"Error loading {file}: {str(e)}")
        return None


def map_team_names(df, teammap):
    if df is None or 'team' not in df.columns:
        return

    print(f"Before team mapping: {df['team'].unique()[:5].tolist()}")

    # Clean team names first
    df["team"] = df["team"].astype(str).str.strip()

    # Apply team mapping if provided
    if teammap:
        df["team"] = df["team"].map(lambda x: teammap.get(x, x))

    # Then standardize to abbreviations
    df["team"] = df["team"].apply(standardize_team_names)

    print(f"After team mapping and standardization: {df['team'].unique()[:5].tolist()}")


def clean_player_data(df):
    if df is None:
        return
    # Clean all string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).replace(r"[^\w\s]|_\*| jr| ii", "", regex=True)


def calculate_average_rank(df, column_names, new_column):
    if df is None:
        return

    # Find columns that actually exist
    existing_cols = []
    for col_name in column_names:
        if col_name in df.columns:
            existing_cols.append(col_name)

    print(f"Calculating {new_column} from columns: {existing_cols}")
    print(f"Available columns in dataframe: {df.columns.tolist()}")

    if existing_cols:
        # Show sample data before calculation
        print(f"Sample data for calculation:")
        for col in existing_cols:
            print(f"  {col}: {df[col].head(3).tolist()}")

        df[new_column] = df[existing_cols].mean(axis=1, numeric_only=True)
        print(f"Calculated {new_column}: {df[new_column].head(3).tolist()}")
    else:
        print(f"Warning: No columns found for average calculation: {column_names}")
        print(f"Available columns: {df.columns.tolist()}")


def standardize_team_names(team_name):
    """Convert team names to standard abbreviations"""
    team_mapping = {
        'ARIZONA CARDINALS': 'ARI', 'CARDINALS': 'ARI', 'AZ': 'ARI',
        'ATLANTA FALCONS': 'ATL', 'FALCONS': 'ATL',
        'BALTIMORE RAVENS': 'BAL', 'RAVENS': 'BAL',
        'BUFFALO BILLS': 'BUF', 'BILLS': 'BUF',
        'CAROLINA PANTHERS': 'CAR', 'PANTHERS': 'CAR',
        'CHICAGO BEARS': 'CHI', 'BEARS': 'CHI',
        'CINCINNATI BENGALS': 'CIN', 'BENGALS': 'CIN',
        'CLEVELAND BROWNS': 'CLE', 'BROWNS': 'CLE',
        'DALLAS COWBOYS': 'DAL', 'COWBOYS': 'DAL',
        'DENVER BRONCOS': 'DEN', 'BRONCOS': 'DEN',
        'DETROIT LIONS': 'DET', 'LIONS': 'DET',
        'GREEN BAY PACKERS': 'GB', 'PACKERS': 'GB',
        'HOUSTON TEXANS': 'HOU', 'TEXANS': 'HOU',
        'INDIANAPOLIS COLTS': 'IND', 'COLTS': 'IND',
        'JACKSONVILLE JAGUARS': 'JAX', 'JAGUARS': 'JAX', 'JAC': 'JAX',
        'KANSAS CITY CHIEFS': 'KC', 'CHIEFS': 'KC', 'KAN': 'KC',
        'LAS VEGAS RAIDERS': 'LV', 'RAIDERS': 'LV', 'LVR': 'LV', 'LAS': 'LV',
        'LOS ANGELES CHARGERS': 'LAC', 'CHARGERS': 'LAC', 'LA CHARGERS': 'LAC',
        'LOS ANGELES RAMS': 'LAR', 'RAMS': 'LAR', 'LA RAMS': 'LAR',
        'MIAMI DOLPHINS': 'MIA', 'DOLPHINS': 'MIA',
        'MINNESOTA VIKINGS': 'MIN', 'VIKINGS': 'MIN',
        'NEW ENGLAND PATRIOTS': 'NE', 'PATRIOTS': 'NE',
        'NEW ORLEANS SAINTS': 'NO', 'SAINTS': 'NO',
        'NEW YORK GIANTS': 'NYG', 'GIANTS': 'NYG', 'NY GIANTS': 'NYG',
        'NEW YORK JETS': 'NYJ', 'JETS': 'NYJ', 'NY JETS': 'NYJ',
        'PHILADELPHIA EAGLES': 'PHI', 'EAGLES': 'PHI',
        'PITTSBURGH STEELERS': 'PIT', 'STEELERS': 'PIT',
        'SAN FRANCISCO 49ERS': 'SF', '49ERS': 'SF', 'SAN FRANCISCO': 'SF',
        'SEATTLE SEAHAWKS': 'SEA', 'SEAHAWKS': 'SEA',
        'TAMPA BAY BUCCANEERS': 'TB', 'BUCCANEERS': 'TB', 'BUCS': 'TB',
        'TENNESSEE TITANS': 'TEN', 'TITANS': 'TEN',
        'WASHINGTON COMMANDERS': 'WAS', 'COMMANDERS': 'WAS', 'WASHINGTON': 'WAS'
    }

    team_clean = str(team_name).strip().upper()
    return team_mapping.get(team_clean, team_clean)


def merge_and_fill_na(df1, df2, on_column, how_type):
    if df1 is None or df2 is None:
        return df1 if df1 is not None else df2

    if on_column not in df1.columns or on_column not in df2.columns:
        print(f"Warning: Column '{on_column}' not found for merging")
        print(f"df1 columns: {df1.columns.tolist()}")
        print(f"df2 columns: {df2.columns.tolist()}")
        return df1

    print(f"Merging on '{on_column}' using {how_type} join")
    print(f"df1 shape before merge: {df1.shape}")
    print(f"df2 shape before merge: {df2.shape}")

    # Clean team names for consistent matching
    df1_clean = df1.copy()
    df2_clean = df2.copy()

    # Standardize team names to abbreviations
    if on_column == 'team':
        df1_clean[on_column] = df1_clean[on_column].apply(standardize_team_names)
        df2_clean[on_column] = df2_clean[on_column].apply(standardize_team_names)

        print(f"Sample standardized teams from df1: {df1_clean[on_column].unique()[:5].tolist()}")
        print(f"Sample standardized teams from df2: {df2_clean[on_column].unique()[:5].tolist()}")

    merged_df = df1_clean.merge(df2_clean, on=[on_column], how=how_type)
    print(f"Merged shape: {merged_df.shape}")

    result = merged_df.fillna(value=0)
    return result


def convert_floats_to_ints(df):
    if df is None:
        return
    float_cols = df.select_dtypes(include=["float64"]).columns
    df[float_cols] = df[float_cols].astype(int)


# Load the team mapping
teammap = {}
if os.path.exists("teamdict.csv"):
    try:
        teammap = pd.read_csv("teamdict.csv", index_col=0).squeeze().to_dict()
        print(f"Loaded team mapping with {len(teammap)} entries")
    except Exception as e:
        print(f"Error loading team mapping: {str(e)}")
        teammap = {}
else:
    print("Warning: teamdict.csv not found. Using empty team mapping.")

# Load and process dataframes with more flexible column matching
print("\n=== Loading Data Files ===")
df_pff_oline = load_and_convert_data("pff-oline.csv", ["team", "pff-rank", "rank"])
df_pfsn_oline = load_and_convert_data("pfsn-oline.csv", ["team", "pfsn-rank", "rank"])
df_pfn_oline = load_and_convert_data("pfn-oline.csv", ["team", "pfn-rank", "rank"])
df_cbs_sos = load_and_convert_data("cbs-sos.csv", ["Team", "team", "cbs-rank", "rank"])
df_sharp_sos = load_and_convert_data("sharp-sos.csv", ["Team", "team", "sharp-rank", "rank"])
df_fgguys_sos = load_and_convert_data("fgguys-sos.csv", ["Team", "team", "fgguys-rank", "rank"])
dfplayer = load_and_convert_data("adp.csv", ["Rank", "rank", "Name", "name", "Team", "team", "Pos", "position"])

print("\n=== Processing Data ===")

# Apply transformations before merging
dataframes = [df_pff_oline, df_pfn_oline, df_cbs_sos, df_pfsn_oline, df_sharp_sos, df_fgguys_sos, dfplayer]
for df in dataframes:
    if df is not None:
        map_team_names(df, teammap)
        convert_floats_to_ints(df)

# Clean player data
clean_player_data(dfplayer)

# Initialize result dataframe
df_players = dfplayer

# Merge offensive line data if available
print("\n=== Processing Offensive Line Data ===")
oline_dfs = [df for df in [df_pfn_oline, df_pff_oline, df_pfsn_oline] if df is not None]

if oline_dfs:
    df_oline = oline_dfs[0].copy()  # Start with first available dataframe

    # Standardize the rank column name for the first dataframe
    rank_cols_to_rename = ['rank', 'pfn-rank', 'pff-rank', 'pfsn-rank']
    first_rank_col = None
    for col in rank_cols_to_rename:
        if col in df_oline.columns:
            if col != 'pfn-rank':  # Rename to pfn-rank if it's not already
                df_oline = df_oline.rename(columns={col: 'pfn-rank'})
            first_rank_col = 'pfn-rank'
            break

    print(f"Starting with dataframe columns: {df_oline.columns.tolist()}")

    # Merge the other offensive line dataframes
    for i, oline_df in enumerate(oline_dfs[1:], 1):
        oline_df_copy = oline_df.copy()

        # Determine the target column name based on which dataframe this is
        if oline_df is df_pff_oline:
            target_col = 'pff-rank'
        elif oline_df is df_pfsn_oline:
            target_col = 'pfsn-rank'
        else:
            target_col = f'rank-{i}'

        # Find the rank column in this dataframe
        rank_col_found = None
        for col in ['rank', 'pff-rank', 'pfsn-rank', 'pfn-rank']:
            if col in oline_df_copy.columns:
                rank_col_found = col
                break

        if rank_col_found:
            # Rename to target column if needed
            if rank_col_found != target_col:
                oline_df_copy = oline_df_copy.rename(columns={rank_col_found: target_col})

            print(f"Merging {target_col} from dataframe with columns: {oline_df_copy.columns.tolist()}")
            df_oline = merge_and_fill_na(df_oline, oline_df_copy[["team", target_col]], "team", "left")

    convert_floats_to_ints(df_oline)

    # Calculate average from all available rank columns
    rank_columns = [col for col in df_oline.columns if 'rank' in col and col != 'oline-rank']
    print(f"Rank columns found for oline average: {rank_columns}")

    calculate_average_rank(df_oline, rank_columns, "oline-rank")
    convert_floats_to_ints(df_oline)

    print(f"Final oline dataframe columns: {df_oline.columns.tolist()}")
    print(f"Sample oline data:\n{df_oline.head()}")

    # Merge with players
    if df_players is not None:
        print(f"Merging oline data with players...")
        print(f"Sample player teams: {df_players['team'].unique()[:5].tolist()}")
        print(f"Sample oline teams: {df_oline['team'].unique()[:5].tolist()}")
        print(f"Teams in common: {set(df_players['team'].unique()) & set(df_oline['team'].unique())}")

        df_players = merge_and_fill_na(df_players, df_oline[["team", "oline-rank"]], "team", "left")
        print(f"Players dataframe after oline merge: {df_players.columns.tolist()}")
        print(f"Sample oline-rank values after merge: {df_players['oline-rank'].head().tolist()}")
else:
    print("No offensive line data available")

# Merge SOS data if available
print("\n=== Processing SOS Data ===")
sos_dataframes = [df for df in [df_cbs_sos, df_sharp_sos, df_fgguys_sos] if df is not None]

if sos_dataframes:
    df_sos = sos_dataframes[0].copy()

    # Standardize the rank column name for the first dataframe
    first_rank_col = None
    for col in ['rank', 'cbs-rank']:
        if col in df_sos.columns:
            if col != 'cbs-rank':
                df_sos = df_sos.rename(columns={col: 'cbs-rank'})
            first_rank_col = 'cbs-rank'
            break

    print(f"Starting SOS with dataframe columns: {df_sos.columns.tolist()}")

    # Merge additional SOS dataframes
    sos_rank_names = ['sharp-rank', 'fgguys-rank']
    for i, sos_df in enumerate(sos_dataframes[1:]):
        sos_df_copy = sos_df.copy()
        target_col = sos_rank_names[i] if i < len(sos_rank_names) else f'sos-rank-{i}'

        # Find the rank column
        rank_col_found = None
        for col in ['rank', 'sharp-rank', 'fgguys-rank', 'cbs-rank']:
            if col in sos_df_copy.columns:
                rank_col_found = col
                break

        if rank_col_found:
            if rank_col_found != target_col:
                sos_df_copy = sos_df_copy.rename(columns={rank_col_found: target_col})

            print(f"Merging {target_col} from SOS dataframe")
            df_sos = merge_and_fill_na(df_sos, sos_df_copy[["team", target_col]], "team", "left")

    convert_floats_to_ints(df_sos)

    # Calculate average from all available rank columns
    rank_columns = [col for col in df_sos.columns if 'rank' in col and col != 'sos-rank']
    print(f"Rank columns found for SOS average: {rank_columns}")

    calculate_average_rank(df_sos, rank_columns, "sos-rank")
    convert_floats_to_ints(df_sos)

    print(f"Final SOS dataframe columns: {df_sos.columns.tolist()}")
    print(f"Sample SOS data:\n{df_sos.head()}")

    # Merge with players
    if df_players is not None:
        print(f"Merging SOS data with players...")
        print(f"Sample player teams: {df_players['team'].unique()[:5].tolist()}")
        print(f"Sample SOS teams: {df_sos['team'].unique()[:5].tolist()}")
        print(f"Teams in common: {set(df_players['team'].unique()) & set(df_sos['team'].unique())}")

        df_players = merge_and_fill_na(df_players, df_sos[["team", "sos-rank"]], "team", "left")
        print(f"Players dataframe after SOS merge: {df_players.columns.tolist()}")
        print(f"Sample sos-rank values after merge: {df_players['sos-rank'].head().tolist()}")
else:
    print("No SOS data available")

if df_players is not None:
    convert_floats_to_ints(df_players)

    # Standardize column names
    column_mapping = {}
    if 'rank' in df_players.columns and 'adp' not in df_players.columns:
        column_mapping['rank'] = 'adp'
    if 'pos' in df_players.columns and 'position' not in df_players.columns:
        column_mapping['pos'] = 'position'
    # Handle different variations of the name column
    name_variations = ['Name', 'NAME', 'player', 'Player', 'PLAYER']
    for name_var in name_variations:
        if name_var in df_players.columns and 'name' not in df_players.columns:
            column_mapping[name_var] = 'name'
            break

    if column_mapping:
        df_players = df_players.rename(columns=column_mapping)

    convert_floats_to_ints(df_players)

    # Calculate player score (only if all required columns exist)
    required_cols = ['name', 'adp', 'oline-rank', 'sos-rank']
    missing_cols = [col for col in required_cols if col not in df_players.columns]

    if not missing_cols:
        df_players["player-score"] = (
                df_players["adp"] + df_players["oline-rank"] + df_players["sos-rank"]
        )

        # Filter out rows where player-score = 0
        df_players_filtered = df_players.query("`player-score` != 0")

        # Sort and organize the columns
        sorted_df = df_players_filtered.sort_values(by=["player-score"])

        available_columns = [col for col in
                             ["name", "team", "position", "adp", "oline-rank", "sos-rank", "player-score"]
                             if col in sorted_df.columns]
        sorted_df = sorted_df[available_columns]

        print("\n=== Final Results ===")
        print(sorted_df)

        # Save to CSV
        output_path = "/Users/muneer78/Downloads/2025FantasyFootballRanks.csv"
        try:
            sorted_df.to_csv(output_path, index=False)
            print(f"\nResults saved to: {output_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            # Try saving to current directory instead
            try:
                sorted_df.to_csv("2025FantasyFootballRanks.csv", index=False)
                print("Results saved to: 2025FantasyFootballRanks.csv (current directory)")
            except Exception as e2:
                print(f"Could not save file: {str(e2)}")

    else:
        print(f"Cannot calculate player scores. Missing columns: {missing_cols}")
        print("Available columns:", df_players.columns.tolist())
        print("\nShowing available data:")
        print(df_players.head())

        # Even if we can't calculate player scores, show the name data
        if 'name' in df_players.columns:
            print("\nPlayer names from adp.csv:")
            name_cols = [col for col in ['name', 'team', 'position'] if col in df_players.columns]
            print(df_players[name_cols].head(10))

else:
    print("No player data available to process.")