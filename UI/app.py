import streamlit as st

st.set_page_config(
    page_title="Algeria Wildfire Risk",
    page_icon="🔥",
    layout="wide"
)


def home():
    st.title("Algeria Wildfire Risk")

    section = st.sidebar.radio(
        "Section",
        ["Project", "Dataset", "Team", "GitHub"]
    )

    st.page_link(update_page, label="Go to Update Test", icon="🔄")

    if section == "Project":
        # >>> paste your existing Project section code here (indented)
        pass
    elif section == "Dataset":
        # >>> paste your existing Dataset section code here
        pass
    elif section == "Team":
        # >>> paste your existing Team section code here
        pass
    elif section == "GitHub":
        # >>> paste your existing GitHub section code here
        pass


home_page = st.Page(home, title="Project", icon="🔥", default=True)
update_page = st.Page("pages/1_Update_Test.py", title="Update Test", icon="🔄")

pg = st.navigation([home_page, update_page])
pg.run()
