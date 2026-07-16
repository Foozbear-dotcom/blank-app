import streamlit as st


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