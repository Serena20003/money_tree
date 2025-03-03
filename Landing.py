import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
# connecting to database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from Signup import Signup

# 0 means signed in, 1 means on login, 2 means on signup
st.session_state.user_status = 0

with st.sidebar:
    if (st.session_state.user_status == 0):
        st.title("Money Tree")
        st.page_link("pages/Home.py", label="Home", icon="👩‍💻")
        st.page_link("pages/Chat.py", label="Chat", icon="👩‍💻")
        st.page_link("pages/Top10.py", label="Top 10", icon="👩‍💻")
        st.page_link("pages/Setting.py", label="Setting", icon="👩‍💻")
        if st.button("Log out"):
            st.session_state.user_status = 1
            st.switch_page("streamlit_app.py")

# pg = st.navigation([st.Page("Home.py"), st.Page("Chat.py"), st.Page("Top10.py"), st.Page("Setting.py")])

uri = "mongodb+srv://" + st.secrets['MONGODB_ROOT_USER_NAME'] + ":" + st.secrets['MONGODB_ROOT_USER_PASSWORD'] + "@cluster0.pa5rn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# items = list(users.find({"email":"scli@usc.edu"}))
# for item in items:
#     st.write(f"{item['email']} is :{item['first_name']}:")
try:
    # Database
    db = client.money_tree
    # Users Collection
    users = db.users
    if (st.session_state.user_status == 0): # logged in
        st.switch_page("pages/Home.py")
    elif (st.session_state.user_status == 1): # login
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("sign up instead"):
            st.session_state.user_status = 2

        if st.button("Log in", type="primary"):
            # verify user information in mongo db
            if username == "test" and password == "test":
                st.session_state.user_status = True
                st.success("Logged in successfully!")
                st.session_state.user_status == 0
                st.switch_page("pages/Home.py")
            else:
                st.error("Incorrect username or password")
    
    else: # signup
        Signup()
    
except Exception as e:
    st.write(e)