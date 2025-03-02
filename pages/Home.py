import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages

st.title("Home")

# with st.sidebar:
#     if (st.session_state.user_status == 0):
#         st.title("Money Tree")
#         st.page_link("pages/Home.py", label="Home", icon="👩‍💻")
#         st.page_link("pages/Chat.py", label="Chat", icon="👩‍💻")
#         st.page_link("pages/Top10.py", label="Top 10", icon="👩‍💻")
#         st.page_link("pages/Setting.py", label="Setting", icon="👩‍💻")
if st.button("Log out"):
    st.session_state.user_status = 1
    st.switch_page("streamlit_app.py")