import streamlit as st
import pandas as pd


def build_venue_config(venue_config_file):
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

        venue_slots = dict(zip(venue_config["Venue"], venue_config["Slots"]))
        venue_groups = dict(zip(venue_config["Venue"], venue_config["Facility"]))

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

    return venue_slots, venue_groups

def show_venue_usage_report(df):
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

    st.dataframe(
        venue_usage,
        hide_index=True,
        use_container_width=True
    )

    return venue_usage

def show_venue_capacity(df, venue_slots):

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

    venue_round_usage["Capacity"] = (
        venue_round_usage["Venue"]
        .map(venue_slots)
        .fillna(2)
        .astype(int)
    )

    venue_round_usage["Status"] = venue_round_usage.apply(
        lambda row:
            "Over Capacity"
            if row["Games Scheduled"] > row["Capacity"]
            else "OK",
        axis=1
    )

    st.dataframe(
        venue_round_usage,
        hide_index=True,
        use_container_width=True
    )

    over_capacity = venue_round_usage[
        venue_round_usage["Status"] == "Over Capacity"
    ]

    if len(over_capacity) == 0:
        st.success("No venue capacity issues found.")
    else:
        st.warning(
            f"Venue capacity issues: {len(over_capacity)}"
        )

    return (
    capacity_games,
    venue_round_usage,
    over_capacity
    )

def show_venue_clash_detection(df, fixture_stage):

    st.subheader("Venue Clash Detection")

    if fixture_stage != "Final Fixture":

        st.info(
            "Skipped for draft fixtures because Date and Time are not required."
        )

        return pd.DataFrame()

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

        st.warning(
            f"Venue/time clashes found: {len(venue_clashes)}"
        )

        st.dataframe(
            venue_clashes,
            hide_index=True,
            use_container_width=True
        )

    return venue_clashes


