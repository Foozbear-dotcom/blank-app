import streamlit as st
import pandas as pd


def show_repair_settings(clean_rounds):

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

    return repair_mode, current_round

def show_overload_investigation(
    capacity_games,
    over_capacity
):

    st.subheader("Venue Overload Investigation Report")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues to investigate."
        )

        return None

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
        hide_index=True,
        use_container_width=True
    )

    return overload_games

def show_return_fixture_finder(
    df,
    overload_games,
    over_capacity
):

    st.subheader("Return Fixture Finder")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no return fixtures to investigate."
        )

        return None

    return_fixture_rows = []

    games_only_for_returns = df[
        (df["Home"].astype(str).str.lower() != "bye") &
        (df["Away"].astype(str).str.lower() != "bye")
    ].copy()

    for _, overloaded_game in overload_games.iterrows():

        home_team = str(overloaded_game["Home"])
        away_team = str(overloaded_game["Away"])
        competition = overloaded_game["Competition"]
        overload_round = overloaded_game["Round"]

        possible_returns = games_only_for_returns[
            (games_only_for_returns["Competition"] == competition) &
            (games_only_for_returns["Home"].astype(str) == away_team) &
            (games_only_for_returns["Away"].astype(str) == home_team)
        ].copy()

        if len(possible_returns) == 0:

            return_fixture_rows.append({
                "Competition": competition,
                "Overload Round": overload_round,
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
                    "Overload Round": overload_round,
                    "Overload Venue": overloaded_game["Venue"],
                    "Home": home_team,
                    "Away": away_team,
                    "Return Found": "Yes",
                    "Return Round": return_game["Round"],
                    "Return Venue": return_game["Venue"]
                })

    return_fixture_report = pd.DataFrame(
        return_fixture_rows
    )

    st.dataframe(
        return_fixture_report,
        hide_index=True,
        use_container_width=True
    )

    return return_fixture_report


def show_flip_candidate_detection(
    return_fixture_report,
    over_capacity,
    repair_mode,
    current_round
):

    st.subheader("Flip Candidate Detection")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no flip candidates to investigate."
        )

        return None

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

        overload_round_number = int(
            row["Overload Round Number"]
        )

        return_round_number = int(
            row["Return Round Number"]
        )

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
        [
            "Sort Order",
            "Competition",
            "Overload Round"
        ]
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

    return flip_candidate_report

def show_flip_impact_analysis(
    flip_candidate_report,
    over_capacity,
    venue_round_usage,
    venue_slots
):

    st.subheader("Flip Impact Analysis")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no flip impacts to analyse."
        )

        return None

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
            (
                venue_round_usage["Round"].astype(str)
                == str(return_round)
            )
            &
            (
                venue_round_usage["Venue"].astype(str)
                == str(return_venue)
            )
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

    return impact_report

def show_repair_score_report(
    impact_report,
    over_capacity
):

    st.subheader("Repair Score Report")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no repair scores to calculate."
        )

        return None

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
            spare_capacity = int(
                row.get("Spare Capacity", 0)
            )
        except:
            spare_capacity = 0

        if spare_capacity >= 2:
            score += 30

        elif spare_capacity == 1:
            score += 20

        if row.get("Recommendation", "") == "Recommended":
            score += 10

        return score

    repair_score_report["Repair Score"] = (
        repair_score_report.apply(
            calculate_repair_score,
            axis=1
        )
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

    return repair_score_report

def show_top_repair_candidates(
    repair_score_report,
    over_capacity
):

    st.subheader("Top Repair Candidates")

    if len(over_capacity) == 0:

        st.success(
            "No overloaded venues, so no repair candidates found."
        )

        return None

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

    return top_candidates