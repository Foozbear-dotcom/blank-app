import streamlit as st
import pandas as pd

st.title("Fixture Analysis Platform")

uploaded_file = st.file_uploader(
    "Upload Fixture File",
    type=["csv", "xlsx"]
)

venue_config_file = st.file_uploader(
    "Upload Venue Config File",
    type=["csv", "xlsx"]
)

seedings_file = st.file_uploader(
    "Upload Seedings File",
    type=["csv", "xlsx"]
)
with st.expander("Upload File Requirements"):

    st.markdown("""
### Fixture File Required Columns

| Column |
|----------|
| Competition |
| Round |
| Home |
| Away |
| Venue |

---

### Venue Config Required Columns

| Column |
|----------|
| Venue |
| Facility |
| Slots |

Example:

| Venue | Facility | Slots |
|--------|----------|-------|
|
""")
if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File Uploaded Successfully")

    fixture_stage = st.radio(
    "Fixture Stage",
    ["Draft Fixture", "Final Fixture"]
)

    # ==================================================
    # FIXTURE UPLOAD VALIDATION
    # ==================================================

    st.subheader("Fixture Upload Validation")

    if fixture_stage == "Draft Fixture":
        required_fixture_columns = [
            "Competition",
            "Round",
            "Home",
            "Away",
            "Venue"
        ]
    else:
        required_fixture_columns = [
            "Competition",
            "Round",
            "Home",
            "Away",
            "Venue",
            "Date",
            "Time"
        ]

    missing_fixture_columns = [
        col for col in required_fixture_columns
        if col not in df.columns
    ]

    if len(missing_fixture_columns) == 0:
        st.success("Fixture file has all required columns.")
    else:
        st.error("Fixture file is missing required columns:")
        st.write(missing_fixture_columns)
        st.stop()


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

    # ==================================================
    # FIXTURE HEALTH DASHBOARD
    # ==================================================

    st.header("Fixture Health Dashboard")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Competitions", len(competitions))

    with col2:
        st.metric("Teams", len(teams))

    with col3:
        st.metric("Venues", len(venues))

    with col4:
        st.metric("Rounds", len(clean_rounds))

    with col5:
        st.metric("Games", len(df))


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
    # VENUE CONFIG
    # ==================================================

    venue_slots = {}
    venue_groups = {}

    if venue_config_file is not None:

        if venue_config_file.name.endswith(".csv"):
            venue_config = pd.read_csv(venue_config_file)
        else:
            venue_config = pd.read_excel(venue_config_file)

        st.success("Venue Config Uploaded Successfully")

        st.subheader("Venue Config Preview")
        st.dataframe(venue_config)

        venue_config["Venue"] = venue_config["Venue"].astype(str)
        venue_config["Facility"] = venue_config["Facility"].astype(str)
        venue_config["Slots"] = venue_config["Slots"].astype(int)

        venue_slots = dict(
            zip(
                venue_config["Venue"],
                venue_config["Slots"]
            )
        )

        venue_groups = dict(
            zip(
                venue_config["Venue"],
                venue_config["Facility"]
            )
        )

    else:

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

        venue_groups = {
            "H-1": "HAW",
            "H-2": "HAW",
            "ASF": "FHC",
            "BSF": "FHC",
            "ESS1": "ESS",
            "ESS2": "ESS"
        }
    
    # ==================================================
    # VENUE CLASH DETECTION
    # ==================================================

    if fixture_stage == "Final Fixture":

        st.subheader("Venue Clash Detection")

        clash_games = df[
            (df["Home"].astype(str).str.lower() != "bye") &
            (df["Away"].astype(str).str.lower() != "bye")
        ].copy()

        clash_games["Venue"] = clash_games["Venue"].astype(str)
        clash_games["Date"] = clash_games["Date"].astype(str)
        clash_games["Time"] = clash_games["Time"].astype(str)

        venue_clashes = (
            clash_games
            .groupby(["Date", "Venue", "Time"])
            .size()
            .reset_index(name="Games Scheduled")
        )

        venue_clashes = venue_clashes[
            venue_clashes["Games Scheduled"] > 1
        ]

        if len(venue_clashes) == 0:
            st.success("No venue/time clashes found.")
        else:
            st.warning(f"Venue/time clashes found: {len(venue_clashes)}")
            st.dataframe(venue_clashes)

    else:

        st.subheader("Venue Clash Detection")
        st.info("Skipped for draft fixtures because Date and Time are not required.")

    # ==================================================
    # VENUE CAPACITY BY ROUND
    # ==================================================

    st.subheader("Venue Capacity By Round")

    capacity_games = df[
        (df["Home"].astype(str).str.lower() != "bye") &
        (df["Away"].astype(str).str.lower() != "bye")
    ].copy()

    capacity_games["Venue"] = capacity_games["Venue"].astype(str)

    venue_round_usage = (
        capacity_games
        .groupby(["Round", "Venue"])
        .size()
        .reset_index(name="Games Scheduled")
    )

    venue_round_usage["Capacity"] = venue_round_usage["Venue"].map(
        venue_slots
    ).fillna(2).astype(int)

    venue_round_usage["Status"] = venue_round_usage.apply(
        lambda row: "Over Capacity"
        if row["Games Scheduled"] > row["Capacity"]
        else "OK",
        axis=1
    )

    st.dataframe(
        venue_round_usage.sort_values(
            ["Status", "Round", "Venue"],
            ascending=[True, True, True]
        )
    )

    over_capacity = venue_round_usage[
        venue_round_usage["Status"] == "Over Capacity"
    ]

    if len(over_capacity) == 0:
        st.success("No venue capacity issues by round found.")
    else:
        st.warning(
            f"Venue capacity issues found: {len(over_capacity)}"
        )
        st.dataframe(over_capacity) 
     # ==================================================
    # SEEDINGS UPLOAD
    # ==================================================

    if seedings_file is not None:

        if seedings_file.name.endswith(".csv"):
            seedings_df = pd.read_csv(seedings_file)
        else:
            seedings_df = pd.read_excel(seedings_file)

        # ==================================================
        # SEEDINGS UPLOAD VALIDATION
        # ==================================================

        st.subheader("Seedings Upload Validation")

        required_seedings_columns = [
            "Competition",
            "Seed",
            "Team",
            "Venue"
        ]

        missing_seedings_columns = [
            col for col in required_seedings_columns
            if col not in seedings_df.columns
        ]

        if len(missing_seedings_columns) == 0:
            st.success("Seedings file has all required columns.")
        else:
            st.error("Seedings file is missing required columns:")
            st.write(missing_seedings_columns)
            st.stop()

        st.success("Seedings File Uploaded Successfully")

        st.subheader("Seedings Preview")
        st.dataframe(seedings_df.head())

        st.subheader("Seedings Summary")

        seed_competitions = (
            seedings_df["Competition"]
            .dropna()
            .astype(str)
            .nunique()
        )

        seed_teams = (
            seedings_df[
                seedings_df["Team"]
                .astype(str)
                .str.lower() != "bye"
            ]["Team"]
            .nunique()
        )

        st.write(f"Competitions: {seed_competitions}")
        st.write(f"Teams: {seed_teams}")

        # ==================================================
        # DUPLICATE SEED DETECTION
        # ==================================================

        st.subheader("Duplicate Seed Detection")

        duplicate_seeds = (
            seedings_df
            .groupby(["Competition", "Seed"])
            .size()
            .reset_index(name="Count")
        )

        duplicate_seeds = duplicate_seeds[
            duplicate_seeds["Count"] > 1
        ]

        if len(duplicate_seeds) == 0:

            st.success("No duplicate seeds found.")

        else:

            st.warning(
                f"Duplicate seeds found: {len(duplicate_seeds)}"
            )

            st.dataframe(duplicate_seeds)

        # ==================================================
        # MISSING SEED DETECTION
        # ==================================================

        st.subheader("Missing Seed Detection")

        missing_seed_rows = []

        for competition in seedings_df["Competition"].dropna().unique():

            comp_df = seedings_df[
                seedings_df["Competition"] == competition
            ].copy()

            # Ignore Bye rows
            comp_df = comp_df[
                comp_df["Team"]
                .astype(str)
                .str.lower() != "bye"
            ]

            seeds = sorted(
                comp_df["Seed"]
                .dropna()
                .astype(int)
                .unique()
            )

            if len(seeds) > 0:

                expected = set(
                    range(min(seeds), max(seeds) + 1)
                )

                actual = set(seeds)

                missing = sorted(
                    expected - actual
                )

                for seed in missing:

                    missing_seed_rows.append({
                        "Competition": competition,
                        "Missing Seed": seed
                    })

        if len(missing_seed_rows) == 0:

            st.success(
                "No missing seeds found."
            )

        else:

            missing_seed_report = pd.DataFrame(
                missing_seed_rows
            )

            st.warning(
                f"Missing seeds found: {len(missing_seed_report)}"
            )

            st.dataframe(
                missing_seed_report
            )

        # ==================================================
        # FIXTURE TEAMS VS SEEDINGS TEAMS
        # ==================================================

        st.subheader("Fixture Teams vs Seedings Teams")

        fixture_team_rows = []

        for competition in competitions:

            comp_fixture = df[
                df["Competition"] == competition
            ].copy()

            comp_home = comp_fixture["Home"].dropna().astype(str)
            comp_away = comp_fixture["Away"].dropna().astype(str)

            comp_fixture_teams = pd.concat([
                comp_home,
                comp_away
            ])

            comp_fixture_teams = comp_fixture_teams[
                comp_fixture_teams.str.lower() != "bye"
            ]

            comp_fixture_teams = set(
                comp_fixture_teams.unique()
            )

            comp_seedings = seedings_df[
                seedings_df["Competition"] == competition
            ].copy()

            comp_seeding_teams = comp_seedings["Team"].dropna().astype(str)

            comp_seeding_teams = comp_seeding_teams[
                comp_seeding_teams.str.lower() != "bye"
            ]

            comp_seeding_teams = set(
                comp_seeding_teams.unique()
            )

            fixture_not_seeded = sorted(
                comp_fixture_teams - comp_seeding_teams
            )

            seeded_not_fixture = sorted(
                comp_seeding_teams - comp_fixture_teams
            )

            for team in fixture_not_seeded:

                fixture_team_rows.append({
                    "Competition": competition,
                    "Team": team,
                    "Issue": "In fixture but not in seedings"
                })

            for team in seeded_not_fixture:

                fixture_team_rows.append({
                    "Competition": competition,
                    "Team": team,
                    "Issue": "In seedings but not in fixture"
                })

        if len(fixture_team_rows) == 0:

            st.success(
                "Fixture teams and seedings teams match."
            )

        else:

            fixture_team_report = pd.DataFrame(
                fixture_team_rows
            )

            st.warning(
                f"Fixture/seedings team mismatches found: {len(fixture_team_report)}"
            )

            st.dataframe(
                fixture_team_report)

        # ==================================================
        # SEED LOOKUP REPORT
        # ==================================================

        st.subheader("Seed Lookup Report")

        seed_lookup = (
            seedings_df[
                ["Competition", "Team", "Seed"]
            ]
            .copy()
        )

        fixture_seed_base = df.copy()

        existing_seed_columns = [
            "Home Seed",
            "Away Seed"
        ]

        fixture_seed_base = fixture_seed_base.drop(
            columns=[
                col for col in existing_seed_columns
                if col in fixture_seed_base.columns
            ],
            errors="ignore"
        )

        home_seed_report = pd.merge(
            fixture_seed_base,
            seed_lookup,
            left_on=["Competition", "Home"],
            right_on=["Competition", "Team"],
            how="left"
        )

        home_seed_report = (
            home_seed_report
            .rename(columns={"Seed": "Home Seed"})
            .drop(columns=["Team"])
        )

        seed_report = pd.merge(
            home_seed_report,
            seed_lookup,
            left_on=["Competition", "Away"],
            right_on=["Competition", "Team"],
            how="left"
        )

        seed_report = (
            seed_report
            .rename(columns={"Seed": "Away Seed"})
            .drop(columns=["Team"])
        )

        seed_report = seed_report[
            [
                "Competition",
                "Round",
                "Home",
                "Home Seed",
                "Away",
                "Away Seed"
            ]
        ]

        st.dataframe(seed_report)

        # ==================================================
        # VENUE LOOKUP REPORT
        # ==================================================

        st.subheader("Venue Lookup Report")

        venue_report = df.copy()

        home_venue_lookup = (
            seedings_df[["Competition", "Team", "Venue"]]
            .drop_duplicates()
            .rename(columns={
                "Team": "Home",
                "Venue": "Home Venue"
            })
        )

        venue_report = venue_report.merge(
            home_venue_lookup,
            on=["Competition", "Home"],
            how="left"
        )

        st.dataframe(
            venue_report[
                [
                    "Competition",
                    "Round",
                    "Home",
                    "Home Venue",
                    "Away"
                ]
            ]
        )

        # ==================================================
        # VENUE EXCEPTION REPORT
        # ==================================================

        st.subheader("Venue Exception Report")

        venue_exceptions = venue_report.copy()

        venue_exceptions = venue_exceptions.rename(
            columns={
                "Home Venue": "Default Venue"
            }
        )

        venue_exceptions = venue_exceptions[
    (venue_exceptions["Home"].astype(str).str.lower() != "bye") &
    (venue_exceptions["Away"].astype(str).str.lower() != "bye")
].copy()

        venue_exceptions["Default Venue"] = (
    venue_exceptions["Default Venue"]
    .fillna("")
    .astype(str)
)

        venue_exceptions["Venue"] = (
    venue_exceptions["Venue"]
    .fillna("")
    .astype(str)
)

        venue_exceptions = venue_exceptions[
    venue_exceptions["Default Venue"]
    != venue_exceptions["Venue"]
].copy()

        if len(venue_exceptions) == 0:
            st.success("No venue exceptions found.")

        else:
            st.warning(
                f"Venue exceptions found: {len(venue_exceptions)}"
            )

            st.dataframe(
                venue_exceptions[
                    [
                        "Competition",
                        "Round",
                        "Home",
                        "Away",
                        "Default Venue",
                        "Venue"
                    ]
                ]
            )

# ==================================================
# VENUE RETURN CANDIDATES
# ==================================================

    st.subheader("Venue Return Candidates")

    st.info(
    "Future version: identifies games that may be able to return to their default venue when capacity becomes available."
)

    # ==================================================
    # HOME / AWAY BALANCE REPORT
    # ==================================================

    st.subheader("Home / Away Balance Report")

    fixture_games = df[
        (df["Home"].astype(str).str.lower() != "bye") &
        (df["Away"].astype(str).str.lower() != "bye")
    ].copy()

    home_counts = (
        fixture_games
        .groupby(["Competition", "Home"])
        .size()
        .reset_index(name="Home Games")
        .rename(columns={"Home": "Team"})
    )

    away_counts = (
        fixture_games
        .groupby(["Competition", "Away"])
        .size()
        .reset_index(name="Away Games")
        .rename(columns={"Away": "Team"})
    )

    home_away_report = pd.merge(
        home_counts,
        away_counts,
        on=["Competition", "Team"],
        how="outer"
    ).fillna(0)

    home_away_report["Home Games"] = (
        home_away_report["Home Games"].astype(int)
    )

    home_away_report["Away Games"] = (
        home_away_report["Away Games"].astype(int)
    )

    home_away_report["Difference"] = (
        home_away_report["Home Games"]
        - home_away_report["Away Games"]
    )

    def home_away_status(diff):

        if abs(diff) >= 4:
            return "Critical"

        elif abs(diff) >= 2:
            return "Warning"

        else:
            return "OK"

    home_away_report["Status"] = (
        home_away_report["Difference"]
        .apply(home_away_status)
    )

    home_away_report = home_away_report.sort_values(
        ["Competition", "Status", "Team"]
    )

    st.dataframe(home_away_report)

    critical_home_away = home_away_report[
        home_away_report["Status"] == "Critical"
    ]

    warning_home_away = home_away_report[
        home_away_report["Status"] == "Warning"
    ]

    if len(critical_home_away) > 0:

        st.error(
            f"Critical home/away imbalances: {len(critical_home_away)}"
        )

        st.dataframe(critical_home_away)

    if len(warning_home_away) > 0:

        st.warning(
            f"Home/away warnings: {len(warning_home_away)}"
        )

        st.dataframe(warning_home_away)

    if (
        len(critical_home_away) == 0
        and
        len(warning_home_away) == 0
    ):

        st.success(
            "No significant home/away imbalances found."
        )
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

    # ==================================================
    # MISSING MATCHUP REPORT
    # ==================================================

    st.subheader("Missing Matchup Report")

    missing_matchups = []

    for competition in competitions:

        comp_games = games_only[
            games_only["Competition"] == competition
        ]

        comp_home = comp_games["Home"].dropna().astype(str)
        comp_away = comp_games["Away"].dropna().astype(str)

        comp_teams = sorted(
            pd.concat([comp_home, comp_away]).unique()
        )

        played_pairs = set(
            zip(
                comp_games["Team A"],
                comp_games["Team B"]
            )
        )

        for i in range(len(comp_teams)):
            for j in range(i + 1, len(comp_teams)):

                team_a = min(comp_teams[i], comp_teams[j])
                team_b = max(comp_teams[i], comp_teams[j])

                if (team_a, team_b) not in played_pairs:
                    missing_matchups.append({
                        "Competition": competition,
                        "Team A": team_a,
                        "Team B": team_b
                    })

    missing_matchups_df = pd.DataFrame(missing_matchups)

    if len(missing_matchups_df) == 0:
        st.success("No missing matchups found.")
    else:
        st.warning(
            f"Missing matchups found: {len(missing_matchups_df)}"
        )
        st.dataframe(missing_matchups_df)

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