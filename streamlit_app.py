import streamlit as st
import pandas as pd

st.title("Sports Fixture Creation App")

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

    # ==================================================
    # FILE SUMMARY
    # ==================================================

    st.subheader("File Summary")

    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    st.write("Column Names:")
    st.write(list(df.columns))

    # ==================================================
    # CORE DATA
    # ==================================================

    competitions = sorted(
        df["Competition"].dropna().astype(str).unique()
    )

    home_teams = df["Home"].dropna().astype(str)
    away_teams = df["Away"].dropna().astype(str)

    all_teams = pd.concat([home_teams, away_teams])
    all_teams = all_teams[
        all_teams.str.lower() != "bye"
    ]

    teams = sorted(all_teams.unique())

    venues = sorted(
        df["Venue"].dropna().astype(str).unique()
    )

    rounds = sorted(
        df["Round"].dropna().unique()
    )

    clean_rounds = [int(r) for r in rounds]

    # ==================================================
    # COMPETITION SUMMARY
    # ==================================================

    st.subheader("Competition Summary")

    st.write(f"Competitions: {len(competitions)}")
    st.write(f"Teams: {len(teams)}")
    st.write(f"Venues: {len(venues)}")
    st.write(f"Rounds: {len(clean_rounds)}")
    st.write(f"Games: {len(df)}")

    # ==================================================
    # COMPETITION BREAKDOWN
    # ==================================================

    st.subheader("Competition Breakdown")

    competition_summary = []

    for competition in competitions:

        comp_df = df[
            df["Competition"] == competition
        ]

        comp_home = comp_df["Home"].dropna().astype(str)
        comp_away = comp_df["Away"].dropna().astype(str)

        comp_teams = pd.concat([comp_home, comp_away])

        comp_teams = comp_teams[
            comp_teams.str.lower() != "bye"
        ]

        competition_summary.append({
            "Competition": competition,
            "Teams": comp_teams.nunique(),
            "Games": len(comp_df)
        })

    summary_df = pd.DataFrame(
        competition_summary
    )

    st.dataframe(summary_df)

    # ==================================================
    # POTENTIAL DATA ISSUES
    # ==================================================

    st.subheader("Potential Data Issues")

    missing_venues = df["Venue"].isna().sum()
    missing_home = df["Home"].isna().sum()
    missing_away = df["Away"].isna().sum()

    st.write(f"Missing Venues: {missing_venues}")
    st.write(f"Missing Home Teams: {missing_home}")
    st.write(f"Missing Away Teams: {missing_away}")

    # ==================================================
    # BYE REPORT
    # ==================================================

    st.subheader("Bye Report")

    home_byes = df[
        df["Home"].astype(str).str.lower() == "bye"
    ]["Away"].astype(str)

    away_byes = df[
        df["Away"].astype(str).str.lower() == "bye"
    ]["Home"].astype(str)

    bye_teams = pd.concat([
        home_byes,
        away_byes
    ])

    bye_counts = (
        bye_teams
        .value_counts()
        .sort_index()
    )

    st.write(
        f"Total Byes Found: {len(bye_teams)}"
    )

    st.dataframe(
        bye_counts.rename("Bye Count")
    )

    # ==================================================
    # PREVIEW
    # ==================================================

    st.subheader("Preview")
    st.dataframe(df.head())

    # ==================================================
    # COMPETITIONS
    # ==================================================

    st.subheader("Competitions Found")

    st.write(
        f"Total Competitions: {len(competitions)}"
    )

    for comp in competitions:
        st.write(comp)

    # ==================================================
    # TEAMS
    # ==================================================

    st.subheader("Teams Found")

    st.write(
        f"Total Teams: {len(teams)}"
    )

    for team in teams:
        st.write(team)

    # ==================================================
    # VENUES
    # ==================================================

    st.subheader("Venues Found")

    st.write(
        f"Total Venues: {len(venues)}"
    )

    for venue in venues:
        st.write(venue)

    # ==================================================
    # ROUNDS
    # ==================================================

    st.subheader("Rounds Found")

    st.write(
        f"Total Rounds: {len(clean_rounds)}"
    )

    st.text(
        ", ".join(
            map(str, clean_rounds)
        )
    )

    comp_df = df[df["Competition"] == competition]

    home_teams = comp_df["Home"].dropna().astype(str)
    away_teams = comp_df["Away"].dropna().astype(str)

    teams_in_comp = pd.concat([home_teams, away_teams])
    teams_in_comp = teams_in_comp[
        teams_in_comp.str.lower() != "bye"
    ]

    competition_summary.append({
        "Competition": competition,
        "Teams": teams_in_comp.nunique(),
        "Games": len(comp_df)
    })

    summary_df = pd.DataFrame(competition_summary)

    st.dataframe(summary_df)

    st.subheader("Preview")
    st.dataframe(df.head())

    st.subheader("Potential Data Issues")

    missing_venues = df["Venue"].isna().sum()
    missing_home = df["Home"].isna().sum()
    missing_away = df["Away"].isna().sum()

    st.write(f"Missing Venues: {missing_venues}")
    st.write(f"Missing Home Teams: {missing_home}")
    st.write(f"Missing Away Teams: {missing_away}")

    # TODO: Competition-specific Bye Report
    
    st.subheader("Bye Report")

    home_byes = df[df["Home"].astype(str).str.lower() == "bye"]["Away"].astype(str)
    away_byes = df[df["Away"].astype(str).str.lower() == "bye"]["Home"].astype(str)

    bye_teams = pd.concat([home_byes, away_byes])
    bye_counts = bye_teams.value_counts().sort_index()

    st.write(f"Total Byes Found: {len(bye_teams)}")

    st.dataframe(bye_counts.rename("Bye Count"))

    st.subheader("Competitions Found")
    st.write(f"Total Competitions: {len(competitions)}")

    for comp in competitions:
        st.write(comp)

    st.subheader("Teams Found")
    st.write(f"Total Teams: {len(teams)}")

    for team in teams:
        st.write(team)

    st.subheader("Venues Found")
    st.write(f"Total Venues: {len(venues)}")

    for venue in venues:
        st.write(venue)

    st.subheader("Rounds Found")
    st.write(f"Total Rounds: {len(clean_rounds)}")
    st.text(", ".join(map(str, clean_rounds)))