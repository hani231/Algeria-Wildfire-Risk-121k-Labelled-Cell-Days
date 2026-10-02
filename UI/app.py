import streamlit as st

st.set_page_config(
    page_title="Algeria Wildfire Risk",
    page_icon="🔥",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Project", "Dataset", "Team", "GitHub"]
)

# Main title
st.title("Streamlit Test")
st.subheader("🔥 Algeria Wildfire Risk")

st.write(
    "A Data Mining and Machine Learning project focused on "
    "wildfire risk classification in Algeria."
)

st.divider()

# Project
if page == "Project":

    st.header("Project")

    st.write(
        """
        Algeria Wildfire Risk is a classification project in the
        field of Data Mining and Machine Learning.

        The project studies environmental and meteorological information
        associated with wildfire events in Algeria.

        Each observation represents a geographic cell observed on a
        particular day. The available information can be explored to
        identify patterns related to wildfire occurrence and to prepare
        data for classification models.

        The overall project involves dataset exploration, data
        preparation, feature analysis, machine learning classification,
        and model evaluation.
        """
    )

    st.info(
        "This Streamlit application is currently only a UI demonstration. "
        "No machine learning model is connected yet."
    )

# Dataset
elif page == "Dataset":

    st.header("Dataset")

    st.write("Algeria Wildfire Risk: 121k Labelled Cell-Days")

    st.write(
        "The dataset contains labelled observations representing "
        "geographic cells observed on different days."
    )

    st.metric("Observations", "12,000")

    st.write("Domain: Data Mining / Machine Learning")
    st.write("Task: Classification")

    st.link_button(
        "Open Dataset on Kaggle",
        "https://www.kaggle.com/datasets/"
        "abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days"
    )

# Team
elif page == "Team":

    st.header("Team")

    st.write("IASD12 — Chef d'équipe — GitHub: @hani231")
    st.write("IASD17 — Membre — GitHub: @MoughitMERZOUK")
    st.write("SIAD03 — Membre — GitHub: @lyesaitikhlef")

# GitHub
elif page == "GitHub":

    st.header("Project Repository")

    st.write(
        "The project source code and development work are maintained "
        "in a public GitHub repository."
    )

    st.link_button(
        "Open GitHub Repository",
        "https://github.com/hani231/"
        "Algeria-Wildfire-Risk-121k-Labelled-Cell-Days"
    )

st.divider()

st.page_link(
    "pages/1_Update_Test.py",
    label="🔄 Go to Update Test"
)

st.caption(
    "Algeria Wildfire Risk — Data Mining / Machine Learning — Classification"
)
