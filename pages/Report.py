import streamlit as st
# # connecting to database
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# uri = "mongodb+srv://" + st.secrets['MONGODB_ROOT_USER_NAME'] + ":" + st.secrets['MONGODB_ROOT_USER_PASSWORD'] + "@cluster0.pa5rn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# st.session_state.isLoading = True
# st.session_state.reportReady = False

st.session_state.stock_names = []
st.session_state.topStock = []
st.session_state.secondStock = []
st.session_state.thirdStock = []

from Start import Setup, DataValidation

Setup()

def GetStockNames():
    # get from function
    st.session_state.stock_names.append("Apple")
    st.session_state.stock_names.append("Bee")
    st.session_state.stock_names.append("Cee")

def ShowStock(rank):
    # make cute display of cards
    # collapsable details to reduce reloading
    st.title("Stock #" + str(rank) + ": " + st.session_state.stock_names[rank])

if 'user_input' not in st.session_state or DataValidation() != None:
    st.write("Please head back to Start page to let us know your investment preferences!")
    if st.button("Take me back!"):
        st.switch_page("Start.py")
else:
    if (st.session_state.name != ""):
        st.title("Hi, " + st.session_state.name + "! Here's your top 3 stocks.")
    st.write(st.session_state.user_input)
    GetStockNames()
    ShowStock(0)
    ShowStock(1)
    ShowStock(2)
    
    
    # while st.session_state.isLoading:
    #     st.spinner(text="Generating Report...")
    #     if st.session_state.reportReady:
    #         st.session_state.isLoading = False
            
