import streamlit as st

st.set_page_config(
    page_title="Algeria Wildfire Risk",
    page_icon="🔥",
    layout="wide"
)

REPO_URL = "https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days"

TEAM = [
    {"code": "IASD12", "name": "Hani", "role": "Chef d'équipe", "github": "hani231"},
    {"code": "IASD17", "name": "Moughit MERZOUK", "role": "Membre", "github": "MoughitMERZOUK"},
    {"code": "SIAD03", "name": "Lyes Ait Ikhlef", "role": "Membre", "github": "lyesaitikhlef"},
]


def home():
    st.title("🔥 Algeria Wildfire Risk")

    # Internal navigation (sections of the main page)
    section = st.sidebar.radio("Section", ["Project", "Dataset", "Team", "GitHub"])

    # Link to the separate page
    st.page_link(update_page, label="Go to Update Test", icon="🔄")

    if section == "Project":
        st.header("Project Description")
        st.write(
            "Algeria Wildfire Risk is a Data Mining and Machine Learning project "
            "focused on wildfire risk classification in Algeria."
        )
        st.write(
            "The project uses environmental and meteorological data associated with "
            "geographic cells observed on different days. The objective is to explore "
            "the data, identify relevant patterns and features, prepare the dataset, "
            "and develop classification models capable of predicting wildfire risk."
        )

        st.subheader("The project covers")
        st.markdown(
            "- Data exploration and analysis\n"
            "- Data preprocessing and preparation\n"
            "- Feature analysis\n"
            "- Classification\n"
            "- Model evaluation"
        )

        st.divider()
        st.subheader("School Project")
        st.write("École Militaire Polytechnique (EMP) — Algeria")
        st.write("**Field:** Data Mining / Machine Learning")
        st.write("**Project type:** Academic project")
        st.write("**Task:** Wildfire risk classification")

    elif section == "Dataset":
        st.header("Dataset")
        st.write(
            "The dataset contains about 121k labelled cell-days: environmental and "
            "meteorological data for geographic cells in Algeria, observed on "
            "different days, and labelled for wildfire risk classification."
        )

    elif section == "Team":
        st.header("Team")
        for member in TEAM:
            st.markdown(
                f"- **{member['name']}** ({member['code']}) — {member['role']} — "
                f"[@{member['github']}](https://github.com/{member['github']})"
            )

    elif section == "GitHub":
        st.header("GitHub Repository")
        st.write(
            "All the code, data and reports of the project are in the repository."
        )
        st.link_button("Open the repository", REPO_URL)


home_page = st.Page(home, title="Project", icon="🔥", default=True)
update_page = st.Page("pages/1_Update_Test.py", title="Update Test", icon="🔄")

pg = st.navigation([home_page, update_page])
pg.run()
