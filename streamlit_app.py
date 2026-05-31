import streamlit as st
import pandas as pd

st.title("Fixture Analysis Platform")

uploaded_file = st.file_uploader(
    "Upload Fixture File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File Uploaded Successfully")

    # File Summary
    st.subheader("File Summary")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")
    st.write("Column Names:")
    st.write(list(df.columns))

    # Core Data
    competitions = sorted(df["Competition"].dropna().astype(str).unique())

    home_teams = df["Home"].dropna().astype(str)
    away_teams = df["Away"].dropna().astype(str)

    all_teams = pd.concat([home_teams, away_teams])
    all_teams = all_teams[all_teams.str.lower() != "bye"]
    teams = sorted(all_teams.unique())

    venues = sorted(df["Venue"].dropna().astype(str).unique())

    rounds = sorted(df["Round"].dropna().unique())
    clean_rounds = [int(r) for r in rounds]

    # Competition Summary
    st.subheader("Competition Summary")
    st.write(f"Competitions: {len(competitions)}")
    st.write(f"Teams: {len(teams)}")
    st.write(f"Venues: {len(venues)}")
    st.write(f"Rounds: {len(clean_rounds)}")
    st.write(f"Games: {len(df)}")

    # Competition Breakdown
    st.subheader("Competition Breakdown")

    competition_summary = []

    for competition in competitions:
        comp_df = df[df["Competition"] == competition]

        comp_home = comp_df["Home"].dropna().astype(str)
        comp_away = comp_df["Away"].dropna().astype(str)

        comp_teams = pd.concat([comp_home, comp_away])
        comp_teams = comp_teams[comp_teams.str.lower() != "bye"]

        competition_summary.append({
            "Competition": competition,
            "Teams": comp_teams.nunique(),
            "Games": len(comp_df)
        })

    summary_df = pd.DataFrame(competition_summary)
    st.dataframe(summary_df)

        # ==================================================
    # COMPETITION RULES REPORT
    # ==================================================

    st.subheader("Competition Rules Report")

    def suggest_matchup_rules(team_count):

        # Round odd team counts up
        if team_count % 2 == 1:
            team_count += 1

        if team_count == 4:
            return 4, 6

        elif team_count == 6:
            return 3, 4

        elif team_count == 8:
            return 2, 3

        elif team_count == 10:
            return 2, 2

        elif team_count == 12:
            return 1, 2

        elif team_count == 14:
            return 1, 2

        elif team_count >= 16:
            return 1, 1

        else:
            return 1, 3
    
    rules_summary = []

    for _, row in summary_df.iterrows():
        min_matchups, max_matchups = suggest_matchup_rules(row["Teams"])

        rules_summary.append({
            "Competition": row["Competition"],
            "Teams": row["Teams"],
            "Suggested Min Matchups": min_matchups,
            "Suggested Max Matchups": max_matchups
        })

    rules_df = pd.DataFrame(rules_summary)

    st.dataframe(rules_df)

        # ==================================================
    # VENUE USAGE REPORT
    # ==================================================

    st.subheader("Venue Usage Report")

    venue_games = df[
        (df["Home"].astype(str).str.lower() != "bye") &
        (df["Away"].astype(str).str.lower() != "bye")
    ].copy()

    venue_games["Venue"] = venue_games["Venue"].astype(str)

    venue_usage = (
        venue_games
        .groupby(["Venue"])
        .size()
        .reset_index(name="Games")
        .sort_values("Games", ascending=False)
    )

    st.dataframe(venue_usage)

    # ==================================================
    # VENUE CAPACITY REPORT
    # ==================================================

    st.subheader("Venue Capacity Report")

    venue_slots = {
        "MBN": 3,
        "MNT": 3,
        "MON": 2,

        "H-1": 2,
        "H-2": 2,

        "ASF": 2,
        "BSF": 2,

        "ESS1": 2,
        "ESS2": 2,

        "HAW": 2,
        "FHC": 2,
        "ESS": 2
    }

    venue_capacity_report = []

    total_rounds = len(clean_rounds)

    for _, row in venue_usage.iterrows():

        venue = row["Venue"]
        games = row["Games"]

        slots = venue_slots.get(venue, 2)

        capacity = slots * total_rounds

        utilisation = round(
            (games / capacity) * 100,
            1
        )

        venue_capacity_report.append({
            "Venue": venue,
            "Games": games,
            "Slots": slots,
            "Capacity": capacity,
            "Utilisation %": utilisation
        })

    venue_capacity_df = pd.DataFrame(
        venue_capacity_report
    )

    st.dataframe(venue_capacity_df)

    # Future: Venue Group Mapping
    # H-1 + H-2 = HAW
    # ASF + BSF = FHC
    # ESS1 + ESS2 = ESS

    # Potential Data Issues
    st.subheader("Potential Data Issues")

    missing_venues = df["Venue"].isna().sum()
    missing_home = df["Home"].isna().sum()
    missing_away = df["Away"].isna().sum()

    st.write(f"Missing Venues: {missing_venues}")
    st.write(f"Missing Home Teams: {missing_home}")
    st.write(f"Missing Away Teams: {missing_away}")

    # Bye Report
    st.subheader("Bye Report")

    home_byes = df[df["Home"].astype(str).str.lower() == "bye"]["Away"].astype(str)
    away_byes = df[df["Away"].astype(str).str.lower() == "bye"]["Home"].astype(str)

    bye_teams = pd.concat([home_byes, away_byes])
    bye_counts = bye_teams.value_counts().sort_index()

    st.write(f"Total Byes Found: {len(bye_teams)}")
    st.dataframe(bye_counts.rename("Bye Count"))

    # Competition-Specific Bye Report
    st.subheader("Competition-Specific Bye Report")

    comp_home_byes = df[
        df["Home"].astype(str).str.lower() == "bye"
    ][["Competition", "Away"]].copy()

    comp_home_byes = comp_home_byes.rename(columns={"Away": "Team"})

    comp_away_byes = df[
        df["Away"].astype(str).str.lower() == "bye"
    ][["Competition", "Home"]].copy()

    comp_away_byes = comp_away_byes.rename(columns={"Home": "Team"})

    comp_byes = pd.concat([comp_home_byes, comp_away_byes])
    comp_byes["Team"] = comp_byes["Team"].astype(str)

    comp_bye_report = (
        comp_byes
        .groupby(["Competition", "Team"])
        .size()
        .reset_index(name="Bye Count")
        .sort_values(["Competition", "Team"])
    )

    st.dataframe(comp_bye_report)

    st.subheader("Competition Expectations")

    for competition in competitions:
        st.write(competition)
        
    # ==================================================
    # MATCHUP FREQUENCY REPORT
    # ==================================================

    st.subheader("Matchup Frequency Report")

    games_only = df[
        (df["Home"].astype(str).str.lower() != "bye") &
        (df["Away"].astype(str).str.lower() != "bye")
    ].copy()

    games_only["Team A"] = games_only.apply(
        lambda row: min(str(row["Home"]), str(row["Away"])),
        axis=1
    )

    games_only["Team B"] = games_only.apply(
        lambda row: max(str(row["Home"]), str(row["Away"])),
        axis=1
    )

    matchup_report = (
        games_only
        .groupby(["Competition", "Team A", "Team B"])
        .size()
        .reset_index(name="Times Played")
        .sort_values(["Competition", "Times Played", "Team A", "Team B"], ascending=[True, False, True, True])
    )

    st.dataframe(matchup_report)

    # ==================================================
    # TRIPLE-UP WARNING
    # ==================================================

    st.subheader("Triple-Up Warnings")

    triple_ups = matchup_report[
        matchup_report["Times Played"] >= 3
    ]

    if len(triple_ups) == 0:
        st.success("No triple-ups found.")
    else:
        st.warning(f"Triple-ups found: {len(triple_ups)}")
        st.dataframe(triple_ups)

    # Preview
    st.subheader("Preview")
    st.dataframe(df.head())

    # Competitions Found
    st.subheader("Competitions Found")
    st.write(f"Total Competitions: {len(competitions)}")

    for comp in competitions:
        st.write(comp)

    # Teams Found
    st.subheader("Teams Found")
    st.write(f"Total Teams: {len(teams)}")

    for team in teams:
        st.write(team)

    # Venues Found
    st.subheader("Venues Found")
    st.write(f"Total Venues: {len(venues)}")

    for venue in venues:
        st.write(venue)

    # Rounds Found
    st.subheader("Rounds Found")
    st.write(f"Total Rounds: {len(clean_rounds)}")
    st.text(", ".join(map(str, clean_rounds)))