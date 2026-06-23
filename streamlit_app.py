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
# ==================================================
# SESSION STATE SETUP
# ==================================================

if "override_decisions" not in st.session_state:
    st.session_state["override_decisions"] = []


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
    # NORMALISE UPLOAD TEMPLATE COLUMNS
    # ==================================================

    df = df.rename(
        columns={
            "Grade": "Competition",
            "Game date": "Date"
        }
    )

    if "Field" in df.columns:
        df["Venue Name"] = df["Venue"]
        df["Venue"] = df["Field"]

    if "Round" in df.columns:
        df["Round"] = (
            df["Round"]
            .astype(str)
            .str.replace("Round", "", case=False, regex=False)
            .str.strip()
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

    # ==================================================
    # OPTIONAL OVERRIDE COLUMNS
    # ==================================================

    if "Override" not in df.columns:
        df["Override"] = "No"

    if "Override Reason" not in df.columns:
        df["Override Reason"] = ""

    if "Override Notes" not in df.columns:
        df["Override Notes"] = ""

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
# FILE DEPENDENCY WARNINGS
# ==================================================

    if uploaded_file is not None and seedings_file is None:

        st.warning(
        "Seedings file not uploaded. Venue Exception, Venue Return and Override reports will not be available."
    )

    if uploaded_file is not None and venue_config_file is None:

        st.warning(
            "Venue Config file not uploaded. Venue Capacity reports require a Venue Config file."
        )

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
    # REPAIR ANALYSIS SETTINGS
    # ==================================================

    st.subheader("Repair Analysis Settings")

    repair_mode = st.radio(
        "Repair timing",
        [
            "Pre-season / all rounds adjustable",
            "Season in progress / earlier rounds locked"
        ]
    )

    current_round = None

    if repair_mode == "Season in progress / earlier rounds locked":

        current_round = int(
    st.number_input(
        "Current round",
        min_value=1,
        max_value=int(max(clean_rounds)),
        value=1,
        step=1
    )
)



    # ==================================================
    # VENUE OVERLOAD INVESTIGATION REPORT
    # ==================================================

    st.subheader("Venue Overload Investigation Report")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues to investigate."
        )

    else:

        overload_games = capacity_games.merge(
            over_capacity[
                [
                    "Round",
                    "Venue",
                    "Games Scheduled",
                    "Capacity"
                ]
            ],
            on=[
                "Round",
                "Venue"
            ],
            how="inner"
        )

        overload_games = overload_games.sort_values(
            [
                "Round",
                "Venue",
                "Competition",
                "Home",
                "Away"
            ]
        )

        st.warning(
            f"Games at overloaded venues: {len(overload_games)}"
        )

        st.dataframe(
            overload_games[
                [
                    "Round",
                    "Venue",
                    "Games Scheduled",
                    "Capacity",
                    "Competition",
                    "Home",
                    "Away"
                ]
            ],
            hide_index=True
        )

    # ==================================================
    # RETURN FIXTURE FINDER
    # ==================================================

    st.subheader("Return Fixture Finder")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no return fixtures to investigate."
        )

    else:

        return_fixture_rows = []

        games_only_for_returns = df[
            (df["Home"].astype(str).str.lower() != "bye") &
            (df["Away"].astype(str).str.lower() != "bye")
        ].copy()

        for _, overloaded_game in overload_games.iterrows():

            home_team = str(overloaded_game["Home"])
            away_team = str(overloaded_game["Away"])
            competition = overloaded_game["Competition"]
            current_round = overloaded_game["Round"]

            possible_returns = games_only_for_returns[
                (games_only_for_returns["Competition"] == competition) &
                (games_only_for_returns["Home"].astype(str) == away_team) &
                (games_only_for_returns["Away"].astype(str) == home_team)
            ].copy()

            if len(possible_returns) == 0:

                return_fixture_rows.append({
                    "Competition": competition,
                    "Overload Round": current_round,
                    "Overload Venue": overloaded_game["Venue"],
                    "Home": home_team,
                    "Away": away_team,
                    "Return Found": "No",
                    "Return Round": "",
                    "Return Venue": ""
                })

            else:

                for _, return_game in possible_returns.iterrows():

                    return_fixture_rows.append({
                        "Competition": competition,
                        "Overload Round": current_round,
                        "Overload Venue": overloaded_game["Venue"],
                        "Home": home_team,
                        "Away": away_team,
                        "Return Found": "Yes",
                        "Return Round": return_game["Round"],
                        "Return Venue": return_game["Venue"]
                    })

        return_fixture_report = pd.DataFrame(return_fixture_rows)

        st.dataframe(
            return_fixture_report,
            hide_index=True
        )

    # ==================================================
    # FLIP CANDIDATE DETECTION
    # ==================================================

    st.subheader("Flip Candidate Detection")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no flip candidates to investigate."
        )

    else:

        flip_candidate_report = return_fixture_report.copy()

        flip_candidate_report["Overload Round Number"] = (
            flip_candidate_report["Overload Round"]
            .astype(str)
            .str.replace("Round", "", case=False, regex=False)
            .str.strip()
            .astype(int)
        )

        flip_candidate_report["Return Round Number"] = pd.to_numeric(
            flip_candidate_report["Return Round"],
            errors="coerce"
        )

        def assess_flip_candidate(row):

            if row["Return Found"] != "Yes":
                return (
                    "No Return Fixture",
                    "No return fixture found",
                    "Closed"
                )

            if pd.isna(row["Return Round Number"]):
                return (
                    "No Return Fixture",
                    "Return round missing or invalid",
                    "Closed"
                )

            overload_round_number = int(row["Overload Round Number"])
            return_round_number = int(row["Return Round Number"])

            if repair_mode == "Pre-season / all rounds adjustable":

                return (
                    "Flip Candidate",
                    "All rounds available for repair",
                    "Open"
                )

            current_round_number = int(current_round)

            overload_played = (
                overload_round_number < current_round_number
            )

            return_played = (
                return_round_number < current_round_number
            )

            if not overload_played and not return_played:

                return (
                    "Flip Candidate",
                    "Both fixtures still in future",
                    "Open"
                )

            if overload_played and not return_played:

                return (
                    "Late Repair Candidate",
                    "Original fixture played, return fixture still available",
                    "Limited"
                )

            if overload_played and return_played:

                return (
                    "Closed",
                    "Both fixtures already played",
                    "Closed"
                )

            return (
                "Review",
                "Manual review required",
                "Limited"
            )

        flip_candidate_report[
            ["Flip Candidate", "Reason", "Repair Window"]
        ] = flip_candidate_report.apply(
            lambda row: pd.Series(
                assess_flip_candidate(row)
            ),
            axis=1
        )

        status_order = {
            "Flip Candidate": 1,
            "Late Repair Candidate": 2,
            "Review": 3,
            "Closed": 4,
            "No Return Fixture": 5
        }

        flip_candidate_report["Sort Order"] = (
            flip_candidate_report["Flip Candidate"]
            .map(status_order)
        )

        flip_candidate_report = flip_candidate_report.sort_values(
            ["Sort Order", "Competition", "Overload Round"]
        )

        st.dataframe(
            flip_candidate_report[
                [
                    "Competition",
                    "Overload Round",
                    "Overload Venue",
                    "Home",
                    "Away",
                    "Return Found",
                    "Return Round",
                    "Return Venue",
                    "Flip Candidate",
                    "Repair Window",
                    "Reason"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

    # ==================================================
    # FLIP IMPACT ANALYSIS
    # ==================================================

    st.subheader("Flip Impact Analysis")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no flip impacts to analyse."
        )

    else:

        impact_rows = []

        for _, row in flip_candidate_report.iterrows():

            if row["Flip Candidate"] not in [
                "Flip Candidate",
                "Late Repair Candidate"
            ]:

                impact_rows.append({
                    "Competition": row["Competition"],
                    "Home": row["Home"],
                    "Away": row["Away"],
                    "Overload Round": row.get("Overload Round", ""),
                    "Return Round": row.get("Return Round", ""),
                    "Return Venue": row.get("Return Venue", ""),
                    "Return Found": row.get("Return Found", ""),
                    "Repair Window": row.get("Repair Window", ""),
                    "Spare Capacity": "",
                    "Recommendation": "Not Eligible",
                    "Reason": row["Reason"]
                })

                continue

            return_round = row["Return Round"]
            return_venue = row["Return Venue"]

            venue_capacity_row = venue_round_usage[
                (venue_round_usage["Round"].astype(str) == str(return_round))
                &
                (venue_round_usage["Venue"].astype(str) == str(return_venue))
            ]

            if len(venue_capacity_row) == 0:

                games_scheduled = 0

                capacity = venue_slots.get(
                    str(return_venue),
                    2
                )

            else:

                games_scheduled = int(
                    venue_capacity_row.iloc[0]["Games Scheduled"]
                )

                capacity = int(
                    venue_capacity_row.iloc[0]["Capacity"]
                )

            spare_capacity = capacity - games_scheduled

            if spare_capacity >= 1:

                recommendation = "Recommended"

                reason = (
                    "Repair candidate exists and return venue has capacity."
                )

            else:

                recommendation = "Review"

                reason = (
                    "Return venue may not have spare capacity."
                )

            impact_rows.append({
                "Competition": row["Competition"],
                "Home": row["Home"],
                "Away": row["Away"],
                "Overload Round": row["Overload Round"],
                "Return Round": return_round,
                "Return Venue": return_venue,
                "Return Found": row["Return Found"],
                "Repair Window": row["Repair Window"],
                "Return Venue Capacity": capacity,
                "Games Scheduled": games_scheduled,
                "Spare Capacity": spare_capacity,
                "Recommendation": recommendation,
                "Reason": reason
            })

        impact_report = pd.DataFrame(
            impact_rows
        )

        impact_display = impact_report[
            [
                "Competition",
                "Home",
                "Away",
                "Overload Round",
                "Return Round",
                "Return Venue",
                "Return Found",
                "Repair Window",
                "Spare Capacity",
                "Recommendation",
                "Reason"
            ]
        ]

        st.dataframe(
            impact_display,
            hide_index=True,
            use_container_width=True
        )





    # ==================================================
    # REPAIR SCORE REPORT
    # ==================================================

    st.subheader("Repair Score Report")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no repair scores to calculate."
        )

    else:

        repair_score_report = impact_report.copy()

        def calculate_repair_score(row):

            score = 0

            if row.get("Repair Window", "") == "Open":
                score += 40

            elif row.get("Repair Window", "") == "Limited":
                score += 20

            if row.get("Return Found", "") == "Yes":
                score += 20

            try:
                spare_capacity = int(row.get("Spare Capacity", 0))
            except:
                spare_capacity = 0

            if spare_capacity >= 2:
                score += 30

            elif spare_capacity == 1:
                score += 20

            if row.get("Recommendation", "") == "Recommended":
                score += 10

            return score

        repair_score_report["Repair Score"] = repair_score_report.apply(
            calculate_repair_score,
            axis=1
        )

        def suggest_repair_action(row):

            if row["Repair Score"] >= 90:
                return "Strong candidate - review first"

            elif row["Repair Score"] >= 70:
                return "Good candidate - check details"

            elif row["Repair Score"] >= 40:
                return "Possible repair - manual review"

            elif row.get("Repair Window", "") == "Closed":
                return "No action - repair window closed"

            else:
                return "Manual repair required"

        repair_score_report["Suggested Action"] = (
            repair_score_report.apply(
                suggest_repair_action,
                axis=1
            )
        )

        st.dataframe(
            repair_score_report[
                [
                    "Competition",
                    "Home",
                    "Away",
                    "Overload Round",
                    "Return Round",
                    "Return Venue",
                    "Return Found",
                    "Repair Window",
                    "Spare Capacity",
                    "Recommendation",
                    "Repair Score",
                    "Suggested Action",
                    "Reason"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

    # ==================================================
    # TOP REPAIR CANDIDATES
    # ==================================================

    st.subheader("Top Repair Candidates")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no repair candidates found."
        )

    else:

        top_candidates = repair_score_report.copy()

        top_candidates = top_candidates.sort_values(
            "Repair Score",
            ascending=False
        )

        top_candidates = top_candidates.head(10)

        st.dataframe(
            top_candidates[
                [
                    "Competition",
                    "Home",
                    "Away",
                    "Overload Round",
                    "Return Round",
                    "Return Venue",
                    "Repair Score",
                    "Recommendation"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

    # ==================================================
    # BEST REPAIR SUMMARY
    # ==================================================

    st.subheader("Best Repair Summary")

    if len(over_capacity) == 0:

        st.info("No repair summary available.")

    else:

        best_repair = repair_score_report.sort_values(
            "Repair Score",
            ascending=False
        ).head(1)

        if len(best_repair) == 0:

            st.info("No repair candidates available.")

        else:

            best = best_repair.iloc[0]

            st.success(
                f"Best repair candidate: {best['Home']} v {best['Away']} "
                f"in Round {best['Overload Round']} "
                f"with score {best['Repair Score']}."
            )

            st.write(
                f"Suggested action: {best['Suggested Action']}"
            )

            st.write(
                f"Return fixture: Round {best['Return Round']} at {best['Return Venue']}"
            )

    # ==================================================
    # MANAGER SUMMARY REPORT
    # ==================================================

    st.subheader("Manager Summary")

    venue_issue_count = len(over_capacity)

    repair_candidate_count = len(
        repair_score_report[
            repair_score_report["Repair Score"] >= 70
        ]
    )

    critical_candidate_count = len(
        repair_score_report[
            repair_score_report["Repair Score"] >= 90
        ]
    )

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric(
            "Venue Capacity Issues",
            venue_issue_count
        )

    with summary_col2:
        st.metric(
            "Good Repair Candidates",
            repair_candidate_count
        )

    with summary_col3:
        st.metric(
            "High Priority Repairs",
            critical_candidate_count
        )

    if venue_issue_count == 0:

        st.success(
            "No venue capacity issues detected."
        )

    elif critical_candidate_count > 0:

        st.warning(
            f"{critical_candidate_count} high-priority repair opportunities identified."
        )

    else:

        st.info(
            "Venue issues exist but no high-confidence repair candidates found."
        )

    # ==================================================
    # REPAIR EXPORT REPORT
    # ==================================================

    st.subheader("Repair Export Report")

    if len(over_capacity) == 0:

        st.info("No repair export available because no venue capacity issues were found.")

    else:

        repair_export = repair_score_report[
            [
                "Competition",
                "Home",
                "Away",
                "Overload Round",
                "Return Round",
                "Return Venue",
                "Return Found",
                "Repair Window",
                "Spare Capacity",
                "Recommendation",
                "Repair Score",
                "Suggested Action",
                "Reason"
            ]
        ].copy()

        repair_export = repair_export.sort_values(
            "Repair Score",
            ascending=False
        )

        st.dataframe(
            repair_export,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            label="Download Repair Export CSV",
            data=repair_export.to_csv(index=False),
            file_name="repair_export.csv",
            mime="text/csv"
        )
    # ==================================================
    # HOME / AWAY REPAIR IMPACT
    # ==================================================

    st.subheader("Home / Away Repair Impact")

    if len(over_capacity) == 0:

        st.info("No home/away repair impact available because no venue capacity issues were found.")

    else:

        repair_impact_rows = []

        games_only_home_away = df[
            (df["Home"].astype(str).str.lower() != "bye") &
            (df["Away"].astype(str).str.lower() != "bye")
        ].copy()

        current_home_counts = (
            games_only_home_away
            .groupby(["Competition", "Home"])
            .size()
            .reset_index(name="Current Home Games")
            .rename(columns={"Home": "Team"})
        )

        current_away_counts = (
            games_only_home_away
            .groupby(["Competition", "Away"])
            .size()
            .reset_index(name="Current Away Games")
            .rename(columns={"Away": "Team"})
        )

        current_balance = pd.merge(
            current_home_counts,
            current_away_counts,
            on=["Competition", "Team"],
            how="outer"
        ).fillna(0)

        current_balance["Current Home Games"] = current_balance["Current Home Games"].astype(int)
        current_balance["Current Away Games"] = current_balance["Current Away Games"].astype(int)

        for _, row in repair_score_report.iterrows():

            if row["Repair Score"] <= 0:
                continue

            competition = row["Competition"]
            home_team = row["Home"]
            away_team = row["Away"]

            home_balance = current_balance[
                (current_balance["Competition"] == competition) &
                (current_balance["Team"] == home_team)
            ]

            away_balance = current_balance[
                (current_balance["Competition"] == competition) &
                (current_balance["Team"] == away_team)
            ]

            if len(home_balance) == 0 or len(away_balance) == 0:
                continue

            home_current_home = int(home_balance.iloc[0]["Current Home Games"])
            home_current_away = int(home_balance.iloc[0]["Current Away Games"])

            away_current_home = int(away_balance.iloc[0]["Current Home Games"])
            away_current_away = int(away_balance.iloc[0]["Current Away Games"])

            home_current_diff = home_current_home - home_current_away
            away_current_diff = away_current_home - away_current_away

            # If flipped, current home team loses one home game and gains one away game.
            home_projected_home = home_current_home - 1
            home_projected_away = home_current_away + 1

            # Current away team gains one home game and loses one away game.
            away_projected_home = away_current_home + 1
            away_projected_away = away_current_away - 1

            home_projected_diff = home_projected_home - home_projected_away
            away_projected_diff = away_projected_home - away_projected_away

            current_total_imbalance = abs(home_current_diff) + abs(away_current_diff)
            projected_total_imbalance = abs(home_projected_diff) + abs(away_projected_diff)

            if projected_total_imbalance < current_total_imbalance:
                impact = "Improves Balance"
            elif projected_total_imbalance == current_total_imbalance:
                impact = "Neutral"
            else:
                impact = "Worsens Balance"

            repair_impact_rows.append({
                "Competition": competition,
                "Home": home_team,
                "Away": away_team,
                "Repair Score": row["Repair Score"],
                "Repair Window": row["Repair Window"],
                "Home Current H/A": f"{home_current_home}/{home_current_away}",
                "Home Projected H/A": f"{home_projected_home}/{home_projected_away}",
                "Away Current H/A": f"{away_current_home}/{away_current_away}",
                "Away Projected H/A": f"{away_projected_home}/{away_projected_away}",
                "Balance Impact": impact
            })

        if len(repair_impact_rows) == 0:

            st.info("No home/away impact rows available.")

        else:

            home_away_repair_impact = pd.DataFrame(repair_impact_rows)

            st.dataframe(
                home_away_repair_impact.sort_values(
                    ["Balance Impact", "Repair Score"],
                    ascending=[True, False]
                ),
                hide_index=True,
                use_container_width=True
            )

    # ==================================================
    # MATCHUP REPAIR IMPACT
    # ==================================================

    st.subheader("Matchup Repair Impact")

    if len(over_capacity) == 0:

        st.info(
            "No matchup repair impact available because no venue capacity issues were found."
        )

    else:

        matchup_rows = []

        games_only = df[
            (df["Home"].astype(str).str.lower() != "bye")
            &
            (df["Away"].astype(str).str.lower() != "bye")
        ].copy()

        games_only["Matchup Key"] = games_only.apply(
            lambda row: " vs ".join(
                sorted([
                    str(row["Home"]),
                    str(row["Away"])
                ])
            ),
            axis=1
        )

        matchup_counts = (
            games_only
            .groupby(
                ["Competition", "Matchup Key"]
            )
            .size()
            .reset_index(name="Current Meetings")
        )

        for _, row in repair_score_report.iterrows():

            competition = row["Competition"]

            matchup_key = " vs ".join(
                sorted([
                    str(row["Home"]),
                    str(row["Away"])
                ])
            )

            matchup_record = matchup_counts[
                (matchup_counts["Competition"] == competition)
                &
                (matchup_counts["Matchup Key"] == matchup_key)
            ]

            if len(matchup_record) == 0:

                current_meetings = 0

            else:

                current_meetings = int(
                    matchup_record.iloc[0]["Current Meetings"]
                )

            if current_meetings <= 2:

                matchup_impact = "Healthy"

            elif current_meetings == 3:

                matchup_impact = "Monitor"

            else:

                matchup_impact = "Overplayed"

            matchup_rows.append({
                "Competition": competition,
                "Home": row["Home"],
                "Away": row["Away"],
                "Repair Score": row["Repair Score"],
                "Current Meetings": current_meetings,
                "Matchup Impact": matchup_impact
            })

        matchup_impact_report = pd.DataFrame(
            matchup_rows
        )

        st.dataframe(
            matchup_impact_report.sort_values(
                ["Repair Score"],
                ascending=False
            ),
            hide_index=True,
            use_container_width=True
        )






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
        # VENUE RETURN OPPORTUNITIES
        # ==================================================

        st.subheader("Venue Return Opportunities")

        venue_return_base = venue_exceptions.copy()

        suppressed_returns = venue_return_base[
            venue_return_base["Override"]
            .astype(str)
            .str.lower()
            == "yes"
        ].copy()

        venue_return_base = venue_return_base[
            venue_return_base["Override"]
            .astype(str)
            .str.lower()
            != "yes"
        ].copy()

        if len(suppressed_returns) > 0:
            st.info(
                f"Venue return opportunities suppressed by override: {len(suppressed_returns)}"
            )

        if len(venue_return_base) == 0:

            st.success("No venue return opportunities found.")

        else:

            venue_return_base["Round Key"] = (
                venue_return_base["Round"].astype(str)
            )

            venue_return_base["Default Venue"] = (
                venue_return_base["Default Venue"].fillna("").astype(str)
            )

            capacity_lookup = venue_round_usage.copy()

            capacity_lookup["Round Key"] = (
                capacity_lookup["Round"].astype(str)
            )

            capacity_lookup["Default Venue"] = (
                capacity_lookup["Venue"].astype(str)
            )

            capacity_lookup = capacity_lookup.rename(
                columns={
                    "Games Scheduled": "Games At Default Venue",
                    "Capacity": "Default Venue Capacity"
                }
            )

            venue_return_base = venue_return_base.merge(
                capacity_lookup[
                    [
                        "Round Key",
                        "Default Venue",
                        "Games At Default Venue",
                        "Default Venue Capacity"
                    ]
                ],
                on=["Round Key", "Default Venue"],
                how="left"
            )

            venue_return_base["Games At Default Venue"] = (
                venue_return_base["Games At Default Venue"]
                .fillna(0)
                .astype(int)
            )

            venue_return_base["Default Venue Capacity"] = (
                venue_return_base["Default Venue Capacity"]
                .fillna(
                    venue_return_base["Default Venue"].map(venue_slots)
                )
                .fillna(2)
                .astype(int)
            )

            venue_return_base["Spare Capacity"] = (
                venue_return_base["Default Venue Capacity"]
                - venue_return_base["Games At Default Venue"]
            )

            venue_return_opportunities = venue_return_base[
                venue_return_base["Spare Capacity"] >= 1
            ].copy()

            if len(venue_return_opportunities) == 0:

                st.info(
                    "No moved games currently have spare capacity at their default venue."
                )

            else:

                st.success(
                    f"Venue return opportunities found: {len(venue_return_opportunities)}"
                )

                st.dataframe(
                    venue_return_opportunities[
                        [
                            "Competition",
                            "Round",
                            "Home",
                            "Away",
                            "Default Venue",
                            "Venue",
                            "Games At Default Venue",
                            "Default Venue Capacity",
                            "Spare Capacity",
                            "Override",
                            "Override Reason",
                            "Override Notes"
                        ]
                    ].rename(
                        columns={
                            "Venue": "Current Venue"
                        }
                    )
                )

        # ==================================================
        # OVERRIDE ASSISTANT UI
        # ==================================================

                st.subheader("Override Assistant")

                if len(venue_return_opportunities) == 0:

                    st.info("No venue return opportunities available for override review.")

                else:

                    venue_return_opportunities["Game Label"] = (
                venue_return_opportunities["Competition"].astype(str)
                + " | Round "
                + venue_return_opportunities["Round"].astype(str)
                + " | "
                + venue_return_opportunities["Home"].astype(str)
                + " v "
                + venue_return_opportunities["Away"].astype(str)
                + " | "
                + venue_return_opportunities["Venue"].astype(str)
                + " → "
                + venue_return_opportunities["Default Venue"].astype(str)
            )

                selected_game = st.selectbox(
                "Select game to review",
                venue_return_opportunities["Game Label"]
            )

                selected_row = venue_return_opportunities[
                venue_return_opportunities["Game Label"] == selected_game
            ].iloc[0]

                st.write("Selected Game")
                st.write(f"Competition: {selected_row['Competition']}")
                st.write(f"Round: {selected_row['Round']}")
                st.write(f"Home: {selected_row['Home']}")
                st.write(f"Away: {selected_row['Away']}")
                st.write(f"Current Venue: {selected_row['Venue']}")
             

        # ==================================================
        # SAVED OVERRIDE DECISIONS
        # ==================================================

        st.subheader("Saved Override Decisions")

        if len(st.session_state["override_decisions"]) == 0:

            st.info(
                "No override decisions saved this session."
            )

        else:

            saved_override_df = pd.DataFrame(
                st.session_state["override_decisions"]
            )

            st.dataframe(
                saved_override_df,
                hide_index=True
            )

            st.download_button(
                label="Download Override Decisions CSV",
                data=saved_override_df.to_csv(index=False),
                file_name="override_decisions.csv",
                mime="text/csv"
            )
            # ==================================================
            # VENUE SNAPSHOT
            # ==================================================

            st.subheader("Venue Snapshot")

            snapshot_col1, snapshot_col2, snapshot_col3 = st.columns(3)

            with snapshot_col1:
                st.metric(
                        "Default Venue",
                        selected_row["Default Venue"]
                    )

            with snapshot_col2:
                st.metric(
                        "Games Scheduled",
                        selected_row["Games At Default Venue"]
                    )

            with snapshot_col3:
                st.metric(
                        "Spare Capacity",
                        selected_row["Spare Capacity"]
                    )

            # ==================================================
            # GAMES CURRENTLY AT DEFAULT VENUE
            # ==================================================

                st.write("Games currently at default venue this round:")

                current_default_venue_games = df[
                (df["Round"].astype(str) == str(selected_row["Round"])) &
                (df["Venue"].astype(str) == str(selected_row["Default Venue"])) &
                (df["Home"].astype(str).str.lower() != "bye") &
                (df["Away"].astype(str).str.lower() != "bye")
            ].copy()

            if len(current_default_venue_games) == 0:

                st.info("No games currently scheduled at this venue in this round.")

            else:

                st.dataframe(
                    current_default_venue_games[
                        [
                            "Competition",
                            "Round",
                            "Home",
                            "Away",
                            "Venue"
                        ]
                    ]
                )

                action = st.radio(
                "Decision",
                [
                    "Return to default venue",
                    "Keep current venue / override"
                ]
            )

                override_reason = st.selectbox(
                "Override Reason",
                [
                    "",
                    "Capacity",
                    "Council Closure",
                    "Turf Closure",
                    "Finals",
                    "Tournament",
                    "School Event",
                    "Manual Decision",
                    "Other"
                ]
            )

                override_notes = st.text_input(
                "Override Notes"
            )

        
            if st.button("Save Override Decision"):

                st.session_state["override_decisions"].append({
        "Competition": selected_row["Competition"],
        "Round": selected_row["Round"],
        "Home": selected_row["Home"],
        "Away": selected_row["Away"],
        "Current Venue": selected_row["Venue"],
        "Default Venue": selected_row["Default Venue"],
        "Decision": action,
        "Override Reason": override_reason,
        "Override Notes": override_notes
    })

            st.success("Override decision saved for this session.")

            st.info(
                "This assistant records the decision on screen only for now. "
                "A future version will write this into the exported fixture."
            )

            # ==================================================
            # MANUAL OVERRIDE REPORT
            # ==================================================

            st.subheader("Manual Override Report")

            override_games = df[
    df["Override"]
    .astype(str)
    .str.lower()
    == "yes"
].copy()

            if len(override_games) == 0:

                    st.success(
        "No manual overrides found."
    )

            else:

                    st.warning(
        f"Manual overrides found: {len(override_games)}"
    )

                    st.dataframe(
        override_games[
            [
                "Competition",
                "Round",
                "Home",
                "Away",
                "Venue",
                "Override Reason",
                "Override Notes"
            ]
        ]
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


            # ==================================================
            # EXPORT OPTIONS
            # ==================================================

            st.subheader("Export Options")

            export_type = st.selectbox(
                    "Select Export Type",
                    [
                        "Basic Fixture CSV",
                        "Competition Upload CSV",
                        "Club View Export",
                        "Internal Review Export"
                    ]
                )

            if export_type == "Basic Fixture CSV":

                    export_df = df.copy()

                    st.download_button(
                        label="Download Basic Fixture CSV",
                        data=export_df.to_csv(index=False),
                        file_name="basic_fixture_export.csv",
                        mime="text/csv"
                    )

            else:

                    st.info(
                        "This export profile is planned for a future version."
                    )