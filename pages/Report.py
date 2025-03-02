import streamlit as st
# # connecting to database
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# uri = "mongodb+srv://" + st.secrets['MONGODB_ROOT_USER_NAME'] + ":" + st.secrets['MONGODB_ROOT_USER_PASSWORD'] + "@cluster0.pa5rn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# st.session_state.isLoading = True
# st.session_state.reportReady = False

from Start import Setup, DataValidation

Setup()

if 'user_input' not in st.session_state or DataValidation() != None:
    st.write("Please head back to Start page to let us know your investment preferences!")
    if st.button("Take me back!"):
        st.switch_page("Start.py")
else:
    if (st.session_state.name != ""):
        st.title("Hi, " + st.session_state.name + "! Here's your top 3 stocks.")
    st.write(st.session_state.user_input)

    # while st.session_state.isLoading:
    #     st.spinner(text="Generating Report...")
    #     if st.session_state.reportReady:
    #         st.session_state.isLoading = False
            
