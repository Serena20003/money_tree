import streamlit as st

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("sign up instead"):
    st.switch_page("pages/Home.py")

if st.button("Log in", type="primary"):
    # verify user information in mongo db
    if username == "test" and password == "test":
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        pg = st.navigation([st.Page("Home.py"), st.Page("Chat.py"), st.Page("Top10.py"), st.Page("Setting.py")])
        pg.run()
    else:
        st.error("Incorrect username or password")