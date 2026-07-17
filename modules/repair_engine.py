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

