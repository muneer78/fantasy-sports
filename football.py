import pandas as pd

def convert_column_headers_to_proper_case(df):
    df.columns = [column.title() for column in df.columns]

def load_and_convert_data(file, columns):
    df = pd.read_csv(file, usecols=columns)
    convert_column_headers_to_proper_case(df)
    return df

def map_team_names(df, teammap):
    df["Team"] = df["Team"].map(lambda x: teammap.get(x, x))

def clean_player_data(df):
    df.replace(r"[^\w\s]|_\*| Jr| II", "", regex=True, inplace=True)

def calculate_average_rank(df, columns, new_column):
    cols = df.columns.drop("Team")
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    df[new_column] = df.iloc[:, columns].mean(axis=1, numeric_only=True)

def merge_and_fill_na(df1, df2, on_column, how_type):
    merged_df = df1.merge(df2, on=[on_column], how=how_type)
    return merged_df.fillna(value=0)

def main():
    dfpff = load_and_convert_data("PFFOLine.csv", ["Team", "PFFRank"])
    dfcbsoline = load_and_convert_data("CBSOLine.csv", ["Team", "CBSOLineRank"])
    dfpfn = load_and_convert_data("PFNOLine.csv", ["Team", "Rank"])
    dfcbs = load_and_convert_data("CBSSportsSOS.csv", ["Team", "CBSRank"])
    dffbs = load_and_convert_data("FBSchedulesSOS.csv", ["TEAM", "FBRank"])
    dfpfnsos = load_and_convert_data("PFNSOS.csv", ["Team", "PFNSOSRank"])
    dfdk = load_and_convert_data("DKSOS.csv", ["Team", "DKRank"])
    dfplayer = load_and_convert_data("Player List.csv", ["Rank", "Player", "Team", "POS"])
    df_laghezza = load_and_convert_data("laghezzaranks.csv", [])
    teammap = pd.read_csv("TeamDict.csv", index_col=0).squeeze().to_dict()

    dataframes = [dfpff, dfpfn, dfcbs, dfcbsoline, dffbs, dfpfnsos, dfdk, dfplayer, df_laghezza]

    for df in dataframes:
        map_team_names(df, teammap)

    clean_player_data(dfplayer)
    clean_player_data(df_laghezza)

    df_oline = merge_and_fill_na(dfpfn, dfpff[["Team", "Pffrank"]], "Team", "left")
    df_oline = merge_and_fill_na(df_oline, dfcbsoline[["Team", "Cbsolinerank"]], "Team", "left")
    calculate_average_rank(df_oline, [1, 2], "Olinerank")

    df_sos = merge_and_fill_na(dfcbs, dffbs[["Team", "Fbrank"]], "Team", "left")
    df_sos = merge_and_fill_na(df_sos, dfdk[["Team", "Dkrank"]], "Team", "left")
    calculate_average_rank(df_sos, [1, 2], "Sosrank")

    df_players = merge_and_fill_na(dfplayer, df_oline[["Team", "Olinerank"]], "Team", "left")
    df_players = merge_and_fill_na(df_players, df_laghezza[["Name", "Ranking"]], "Player", "left")
    df_players = merge_and_fill_na(df_players, df_sos[["Team", "Sosrank"]], "Team", "left")
    df_players.drop(columns=['Name'], inplace=True)

    df_players = df_players.rename(columns={"Rank": "ADP", "Player": "Name", "Pos": "Position", "Ranking": "LagRank"})

    calculate_average_rank(df_players, [1, 3, 4], "PlayerScore")

    sorted_df = df_players.sort_values(by=["PlayerScore"])
    new_order = ["Name", "Team", "Position", "Olinerank", "Sosrank", "LagRank", "PlayerScore"]
    sorted_df = sorted_df[new_order]

    sorted_df.to_csv("FantasyFootballRanks.csv", index=False)

if __name__ == "__main__":
    main()
