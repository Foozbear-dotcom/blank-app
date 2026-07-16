import streamlit as st
import pandas as pd


def validate_fixture_upload(df, fixture_stage):

    # --------------------------------------------------
    # Normalise common upload column names
    # --------------------------------------------------

    df = df.rename(
        columns={
            "Grade": "Competition",
            "Game date": "Date"
        }
    )

    if "Field" in df.columns:

        if "Venue" in df.columns:
            df["Venue Name"] = df["Venue"]

        df["Venue"] = df["Field"]

    if "Round" in df.columns:

        df["Round"] = (
            df["Round"]
            .astype(str)
            .str.replace(
                "Round",
                "",
                case=False,
                regex=False
            )
            .str.strip()
        )

    # --------------------------------------------------
    # Validate required columns
    # --------------------------------------------------

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
        column
        for column in required_fixture_columns
        if column not in df.columns
    ]

    if len(missing_fixture_columns) == 0:

        st.success(
            "Fixture file has all required columns."
        )

    else:

        st.error(
            "Fixture file is missing required columns:"
        )

        st.write(missing_fixture_columns)

        st.stop()

    # --------------------------------------------------
    # Add optional override columns when absent
    # --------------------------------------------------

    if "Override" not in df.columns:
        df["Override"] = "No"

    if "Override Reason" not in df.columns:
        df["Override Reason"] = ""

    if "Override Notes" not in df.columns:
        df["Override Notes"] = ""

    return df