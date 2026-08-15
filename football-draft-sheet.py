"""
Football Draft Sheet ETL Pipeline - DuckDB Edition

Expected file structure:
  - oline1.csv, oline2.csv, oline3.csv (offensive line rankings)
    ├─ Must have 'team' column
    ├─ Must have 'oline1rank', 'oline2rank', 'oline3rank' columns respectively
    └─ Script auto-detects which files exist (checks oline1-9.csv)
  
  - sos1.csv, sos2.csv, sos3.csv (strength of schedule)
    ├─ Must have 'team' column
    ├─ Must have 'sos1rank', 'sos2rank', 'sos3rank' columns respectively
    ├─ Rankings are REVERSED during load (33 - original_rank)
    │  so #32 (hardest schedule) → 1 (worst) and #1 (easiest) → 32 (best)
    └─ Script auto-detects which files exist (checks sos1-9.csv)
  
  - adp.csv (player data)
    ├─ "PLAYER NAME" column (player name)
    ├─ TEAM column
    ├─ "POS" column (position)
    └─ "RK" column (rank/ADP - average draft position)
  
  - teamdict.csv (optional, for team name mapping)
    └─ CSV with original team name -> standard abbreviation mapping

Example file structures:

oline1.csv:
  team,oline1rank,other_data
  KC,5,some_value
  LAC,12,another_value

sos1.csv (original):
  team,sos1rank,other_data
  KC,32,some_value    # easiest schedule (becomes 1 after reversal)
  LAC,15,another_value # (becomes 18 after reversal: 33 - 15)

adp.csv (actual structure):
  RK,TIERS,PLAYER NAME,TEAM,POS,BYE WEEK,UPSIDE,BUST,SOS SEASON,ECR VS. ADP
  1,1,Ja'Marr Chase,CIN,WR1,6,5 out of 5,1 out of 5,4 out of 5 stars,+2
  2,1,Patrick Mahomes,KC,QB,5,5 out of 5,1 out of 5,5 out of 5 stars,+1
"""

import duckdb
import os
import re


# ============================================================================
# TEAM MAPPING AND STANDARDIZATION
# ============================================================================

def standardize_team_names(team_name: str) -> str:
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


def clean_string_value(value: str) -> str:
    """Clean string by removing special characters"""
    if value is None:
        return value
    value_str = str(value).strip()
    # Remove special characters except spaces
    cleaned = re.sub(r"[^\w\s]|_\*| jr| ii", "", value_str, flags=re.IGNORECASE)
    return cleaned.strip()


# ============================================================================
# DUCKDB CONNECTION AND SETUP
# ============================================================================

def init_duckdb():
    """Initialize DuckDB connection and register UDFs"""
    conn = duckdb.connect(":memory:")
    
    # Register custom functions for use in SQL
    conn.create_function("standardize_team", standardize_team_names, [str], str)
    conn.create_function("clean_string", clean_string_value, [str], str)
    
    return conn


# ============================================================================
# DATA LOADING
# ============================================================================

def safe_load_csv(conn, filepath: str, expected_columns: list = None) -> str | None:
    """
    Safely load CSV into DuckDB table. Returns table name if successful, None otherwise.
    Handles quoted and unquoted column headers.
    """
    if not os.path.exists(filepath):
        print(f"Warning: File {filepath} not found. Skipping...")
        return None

    try:
        # Generate table name from filepath
        table_name = os.path.splitext(os.path.basename(filepath))[0]
        
        # Read CSV with proper quote handling for mixed quoted/unquoted headers
        conn.execute(f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_csv(
                '{filepath}',
                delim = ',',
                quote = '"',
                escape = '"',
                header = true,
                strict_mode = false,
                null_padding = true
            )
        """)
        
        # Get actual columns
        result = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        actual_columns = [row[1].lower() for row in result]
        
        print(f"✓ Loaded {filepath}")
        print(f"  Available columns: {actual_columns}")
        if expected_columns:
            print(f"  Expected columns: {expected_columns}")
        
        return table_name
        
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None


def load_team_mapping(conn, filepath: str = "teamdict.csv") -> dict:
    """Load team mapping from CSV if available"""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Using empty team mapping.")
        return {}
    
    try:
        result = duckdb.read_csv(
            filepath,
            delim = ',',
            quotechar = '"',
            escape = '"',
            strict_mode = False,
            null_padding = True
        )
        # Convert to dict - assumes first column is key, second is value
        teammap = {}
        for row in result.fetchall():
            if len(row) >= 2:
                teammap[str(row[0])] = str(row[1])
        print(f"✓ Loaded team mapping with {len(teammap)} entries")
        return teammap
    except Exception as e:
        print(f"Error loading team mapping: {str(e)}")
        return {}


# ============================================================================
# DATA TRANSFORMATION PIPELINES
# ============================================================================

def normalize_oline_data(conn, oline_file_indices: list[int]) -> str | None:
    """
    Merge and normalize offensive line data from oline[N].csv files.
    Expects files like oline1.csv, oline2.csv, oline3.csv with rank columns
    like oline1rank, oline2rank, oline3rank.
    
    Args:
        conn: DuckDB connection
        oline_file_indices: List of integers (e.g., [1, 2, 3])
    
    Returns:
        Final table name or None
    """
    if not oline_file_indices:
        print("No offensive line data available")
        return None
    
    print("\n=== Processing Offensive Line Data ===")
    
    # Load and normalize each oline file
    oline_tables = {}
    for idx in oline_file_indices:
        filepath = f"oline{idx}.csv"
        rank_col = f"oline{idx}rank"
        
        if not os.path.exists(filepath):
            print(f"  Warning: {filepath} not found")
            continue
        
        try:
            # First, create a temp table to inspect columns
            temp_table = f"oline{idx}_temp"
            conn.execute(f"""
                CREATE TABLE {temp_table} AS 
                SELECT * FROM read_csv(
                    '{filepath}',
                    delim = ',',
                    quote = '"',
                    escape = '"',
                    header = true,
                    strict_mode = false,
                    null_padding = true
                )
            """)
            
            # Check if expected rank column exists
            result = conn.execute(f"PRAGMA table_info({temp_table})").fetchall()
            actual_columns = {row[1].lower(): row[1] for row in result}
            
            # Find the rank column (look for oline{idx}rank or fallback to 'rank')
            found_rank_col = None
            if rank_col.lower() in actual_columns:
                found_rank_col = actual_columns[rank_col.lower()]
            elif 'rank' in actual_columns:
                found_rank_col = actual_columns['rank']
            
            if not found_rank_col:
                print(f"  Error: No rank column found in {filepath}")
                print(f"    Expected: {rank_col}, Available: {list(actual_columns.values())}")
                conn.execute(f"DROP TABLE {temp_table}")
                continue
            
            # Now create the actual table with transformation
            table_name = f"oline{idx}"
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT 
                    standardize_team(team) as team,
                    CAST("{found_rank_col}" AS INTEGER) as {rank_col}
                FROM {temp_table}
            """)
            conn.execute(f"DROP TABLE {temp_table}")
            
            oline_tables[idx] = table_name
            print(f"  ✓ Loaded {filepath} with rank column: {found_rank_col}")
        except Exception as e:
            print(f"  Error loading {filepath}: {str(e)}")
    
    if not oline_tables:
        return None
    
    # Start with first table
    sorted_indices = sorted(oline_tables.keys())
    working_table = oline_tables[sorted_indices[0]]
    
    # Merge additional tables
    for idx in sorted_indices[1:]:
        rank_col = f"oline{idx}rank"
        merged_table = f"oline_merged_{idx}"
        
        # Select all existing columns from working table plus new rank column
        conn.execute(f"""
            CREATE TABLE {merged_table} AS
            SELECT 
                w.*,
                COALESCE(o.{rank_col}, 0) as {rank_col}
            FROM {working_table} w
            LEFT JOIN {oline_tables[idx]} o ON w.team = o.team
        """)
        
        working_table = merged_table
        print(f"  Merged oline{idx}rank")
    
    # Calculate average rank from all rank columns
    rank_col_names = [f"oline{idx}rank" for idx in sorted_indices]
    rank_cols_sum = ' + '.join(rank_col_names)
    
    final_table = "oline_final"
    conn.execute(f"""
        CREATE TABLE {final_table} AS
        SELECT 
            team,
            {', '.join(rank_col_names)},
            CAST(({rank_cols_sum}) / {len(rank_col_names)} AS INTEGER) as "oline-rank"
        FROM {working_table}
    """)
    
    print(f"✓ Created oline-rank (average of {len(rank_col_names)} sources)")
    return final_table


def normalize_sos_data(conn, sos_file_indices: list[int]) -> str | None:
    """
    Merge and normalize strength of schedule data from sos[N].csv files.
    Expects files like sos1.csv, sos2.csv, sos3.csv with rank columns
    like sos1rank, sos2rank, sos3rank.
    
    NOTE: SOS rankings are reversed during load since #32 (hardest schedule)
    should be lower quality and #1 (easiest schedule) should be higher quality
    for fantasy purposes. Conversion: new_rank = 33 - original_rank
    
    Args:
        conn: DuckDB connection
        sos_file_indices: List of integers (e.g., [1, 2, 3])
    
    Returns:
        Final table name or None
    """
    if not sos_file_indices:
        print("No SOS data available")
        return None
    
    print("\n=== Processing SOS Data ===")
    
    # Load and normalize each sos file
    sos_tables = {}
    for idx in sos_file_indices:
        filepath = f"sos{idx}.csv"
        rank_col = f"sos{idx}rank"
        
        if not os.path.exists(filepath):
            print(f"  Warning: {filepath} not found")
            continue
        
        try:
            # First, create a temp table to inspect columns
            temp_table = f"sos{idx}_temp"
            conn.execute(f"""
                CREATE TABLE {temp_table} AS 
                SELECT * FROM read_csv(
                    '{filepath}',
                    delim = ',',
                    quote = '"',
                    escape = '"',
                    header = true,
                    strict_mode = false,
                    null_padding = true
                )
            """)
            
            # Check if expected rank column exists
            result = conn.execute(f"PRAGMA table_info({temp_table})").fetchall()
            actual_columns = {row[1].lower(): row[1] for row in result}
            
            # Find the rank column (look for sos{idx}rank or fallback to 'rank')
            found_rank_col = None
            if rank_col.lower() in actual_columns:
                found_rank_col = actual_columns[rank_col.lower()]
            elif 'rank' in actual_columns:
                found_rank_col = actual_columns['rank']
            
            if not found_rank_col:
                print(f"  Error: No rank column found in {filepath}")
                print(f"    Expected: {rank_col}, Available: {list(actual_columns.values())}")
                conn.execute(f"DROP TABLE {temp_table}")
                continue
            
            # Now create the actual table with transformation
            table_name = f"sos{idx}"
            # Reverse rankings: #32 (easiest) becomes #1 (best)
            # Assumes 32 teams: new_rank = 33 - original_rank
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT 
                    standardize_team(team) as team,
                    CAST(33 - CAST("{found_rank_col}" AS INTEGER) AS INTEGER) as {rank_col}
                FROM {temp_table}
            """)
            conn.execute(f"DROP TABLE {temp_table}")
            
            sos_tables[idx] = table_name
            print(f"  ✓ Loaded {filepath} with rank column: {found_rank_col} (reversed)")
        except Exception as e:
            print(f"  Error loading {filepath}: {str(e)}")
    
    if not sos_tables:
        return None
    
    # Start with first table
    sorted_indices = sorted(sos_tables.keys())
    working_table = sos_tables[sorted_indices[0]]
    
    # Merge additional tables
    for idx in sorted_indices[1:]:
        rank_col = f"sos{idx}rank"
        merged_table = f"sos_merged_{idx}"
        
        # Select all existing columns from working table plus new rank column
        conn.execute(f"""
            CREATE TABLE {merged_table} AS
            SELECT 
                w.*,
                COALESCE(o.{rank_col}, 0) as {rank_col}
            FROM {working_table} w
            LEFT JOIN {sos_tables[idx]} o ON w.team = o.team
        """)
        
        working_table = merged_table
        print(f"  Merged sos{idx}rank")
    
    # Calculate average rank from all rank columns
    rank_col_names = [f"sos{idx}rank" for idx in sorted_indices]
    rank_cols_sum = ' + '.join(rank_col_names)
    
    final_table = "sos_final"
    conn.execute(f"""
        CREATE TABLE {final_table} AS
        SELECT 
            team,
            {', '.join(rank_col_names)},
            CAST(({rank_cols_sum}) / {len(rank_col_names)} AS INTEGER) as "sos-rank"
        FROM {working_table}
    """)
    
    print(f"✓ Created sos-rank (average of {len(rank_col_names)} sources)")
    return final_table


def normalize_player_data(conn, players_table: str, oline_table: str = None, sos_table: str = None) -> str | None:
    """
    Normalize player data and merge with oline and SOS data.
    Handles various column name formats from adp.csv
    """
    if not players_table:
        print("No player data available")
        return None
    
    print("\n=== Processing Player Data ===")
    
    # Get actual column names from the table
    result = conn.execute(f"PRAGMA table_info({players_table})").fetchall()
    actual_columns = {row[1].lower(): row[1] for row in result}
    
    # Find the correct column names (case-insensitive matching)
    name_col = None
    rank_col = None
    team_col = None
    pos_col = None
    
    for col_lower, col_actual in actual_columns.items():
        if col_lower in ["player name", "name", "player"]:
            name_col = col_actual
        elif col_lower in ["rk", "rank", "adp"]:
            rank_col = col_actual
        elif col_lower in ["team"]:
            team_col = col_actual
        elif col_lower in ["pos", "position"]:
            pos_col = col_actual
    
    if not all([name_col, rank_col, team_col, pos_col]):
        print(f"Error: Missing required columns")
        print(f"  name_col: {name_col}")
        print(f"  rank_col: {rank_col}")
        print(f"  team_col: {team_col}")
        print(f"  pos_col: {pos_col}")
        print(f"  Available columns: {list(actual_columns.values())}")
        return None
    
    # Clean and standardize player data
    working_table = "players_cleaned"
    conn.execute(f"""
        CREATE TABLE {working_table} AS
        SELECT 
            clean_string("{name_col}") as name,
            standardize_team("{team_col}") as team,
            LOWER("{pos_col}") as position,
            CAST("{rank_col}" AS INTEGER) as adp
        FROM {players_table}
        WHERE "{name_col}" IS NOT NULL AND "{rank_col}" IS NOT NULL
    """)
    
    print(f"✓ Cleaned player names, teams, and positions")
    print(f"  Mapped columns: name='{name_col}', team='{team_col}', position='{pos_col}', adp='{rank_col}'")
    
    # Merge offensive line data if available
    if oline_table:
        merged_table = "players_with_oline"
        conn.execute(f"""
            CREATE TABLE {merged_table} AS
            SELECT 
                p.*,
                COALESCE(o."oline-rank", 0) as "oline-rank"
            FROM {working_table} p
            LEFT JOIN {oline_table} o ON p.team = o.team
        """)
        working_table = merged_table
        print("✓ Merged offensive line data")
    
    # Merge SOS data if available
    if sos_table:
        merged_table = "players_with_sos"
        conn.execute(f"""
            CREATE TABLE {merged_table} AS
            SELECT 
                p.*,
                COALESCE(s."sos-rank", 0) as "sos-rank"
            FROM {working_table} p
            LEFT JOIN {sos_table} s ON p.team = s.team
        """)
        working_table = merged_table
        print("✓ Merged SOS data")
    
    # Calculate player score
    score_table = "players_final"
    conn.execute(f"""
        CREATE TABLE {score_table} AS
        SELECT 
            name,
            team,
            position,
            adp,
            "oline-rank" as oline_rank,
            "sos-rank" as sos_rank,
            (adp + COALESCE("oline-rank", 0) + COALESCE("sos-rank", 0)) as "player-score"
        FROM {working_table}
        WHERE (adp + COALESCE("oline-rank", 0) + COALESCE("sos-rank", 0)) != 0
        ORDER BY "player-score" ASC
    """)
    
    print("✓ Calculated player scores")
    return score_table


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("Football Draft Sheet ETL (DuckDB)")
    print("=" * 60)
    
    # Initialize DuckDB
    conn = init_duckdb()
    print("✓ Initialized DuckDB with custom functions\n")
    
    # Load team mapping
    teammap = load_team_mapping(conn)
    
    # Load data files
    print("\n=== Loading Data Files ===")
    
    # Offensive line data - detect which oline[N].csv files exist
    oline_indices = []
    for i in range(1, 10):  # Check oline1.csv through oline9.csv
        if os.path.exists(f"oline{i}.csv"):
            oline_indices.append(i)
    
    # SOS data - detect which sos[N].csv files exist
    sos_indices = []
    for i in range(1, 10):  # Check sos1.csv through sos9.csv
        if os.path.exists(f"sos{i}.csv"):
            sos_indices.append(i)
    
    # Player data - uses actual column names from adp.csv
    players_table = safe_load_csv(conn, "adp.csv", ["PLAYER NAME", "TEAM", "POS", "RK"])
    
    # Process data
    oline_final = normalize_oline_data(conn, oline_indices)
    sos_final = normalize_sos_data(conn, sos_indices)
    players_final = normalize_player_data(conn, players_table, oline_final, sos_final)
    
    # Export results
    if players_final:
        print("\n=== Final Results ===")
        results = conn.execute(f"SELECT * FROM {players_final}").fetchall()
        columns = [desc[0] for desc in conn.execute(f"SELECT * FROM {players_final}").description]
        
        # Print table
        print()
        print("  ".join(f"{col:20}" for col in columns))
        print("-" * (len(columns) * 22))
        for row in results[:20]:  # Show first 20
            print("  ".join(f"{str(val):20}" for val in row))
        
        if len(results) > 20:
            print(f"... and {len(results) - 20} more rows")
        
        # Save to CSV
        output_path = "/Users/muneer78/Downloads/FantasyFootballRanks.csv"
        try:
            conn.execute(f"COPY {players_final} TO '{output_path}' (FORMAT CSV, HEADER TRUE)")
            print(f"\n✓ Results saved to: {output_path}")
        except Exception as e:
            print(f"Error saving to {output_path}: {str(e)}")
            # Try current directory
            try:
                conn.execute(f"COPY {players_final} TO 'FantasyFootballRanks.csv' (FORMAT CSV, HEADER TRUE)")
                print("✓ Results saved to: FantasyFootballRanks.csv (current directory)")
            except Exception as e2:
                print(f"Could not save file: {str(e2)}")
    else:
        print("Could not process player data")
    
    conn.close()


if __name__ == "__main__":
    main()
