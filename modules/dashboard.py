import streamlit as st
import pandas as pd


def show_dashboard(
    df,
    competitions,
    teams,
    venues,
    clean_rounds
):

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

    st.subheader("Competition Breakdown")

    competition_summary = []

    for competition in competitions:

        comp_df = df[df["Competition"] == competition]

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

    summary_df = pd.DataFrame(competition_summary)

    st.dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True
    )

    return summary_df