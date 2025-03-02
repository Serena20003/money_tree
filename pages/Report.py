import streamlit as st
# # connecting to database
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# uri = "mongodb+srv://" + st.secrets['MONGODB_ROOT_USER_NAME'] + ":" + st.secrets['MONGODB_ROOT_USER_PASSWORD'] + "@cluster0.pa5rn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# st.session_state.isLoading = True
# st.session_state.reportReady = False

st.session_state.stocks = []
# test
st.session_state.predictions = []

from Start import Setup, DataValidation
from algorithm import match_investors
from database import User, Investment, get_investments_from_csv
# from trainedml_crypto import crypto_model
# from trainedml_etf import etf_model
# from trainedml_stocks import stock_model

Setup()

def GetStocks():
    # get from function
    user = User()
    user.parse_information_tester(st.session_state.user_input)
    # get investment info
    if ('opportunities' not in st.session_state):
        st.session_state.opportunities = get_investments_from_csv()
    st.session_state.stocks = match_investors(user, st.session_state.opportunities)

# def SetStockPrediction(rank, ticker, type):
    # if (type == "ETF"):
    #     st.session_state.predictions[rank] = etf_model(ticker) # list of 3,6,9,12,15,18,21 month prediction based on the ticker
    # else:
    #     st.session_state.predictions[rank] = crypto_model(ticker) # list of 3,6,9,12,15,18,21 month prediction based on the ticker

def ShowStock(rank):
    # make cute display of cards
    # collapsable details to reduce reloading
    st.header("Investment #" + str(rank+1) + ": " + st.session_state.stocks[rank][1].name)
    # if crypto, etf
    if st.session_state.stocks[rank][1].asset_type == "ETF" or st.session_state.stocks[rank][1].asset_type == "Crypto":
        if ('predictions' not in st.session_state):
            SetStockPrediction(rank, st.session_state.stocks[rank][1].ticker, st.session_state.stocks[rank][1].asset_type)
        st.subheader("Predictions")
        col1, col2 = st.columns(2, border=True)
        # most recent prediction
        mstRecent = ""
        st.session_state.predictions = [[33,27], [33,33],[3,29]]
        if (st.session_state.predictions[rank][0] < 0):
            mstRecent = "-"
        mstRecent += "$" + str(abs(st.session_state.predictions[rank][0]))
        col1.metric("3 months", mstRecent)
        # second most recent prediction
        mst2Recent = ""
        if (st.session_state.predictions[rank][1] < 0):
            mst2Recent = "-"
        mst2Recent += "$" + str(abs(st.session_state.predictions[rank][1]))
        col2.metric("6 months", mst2Recent, str((st.session_state.predictions[rank][1]-st.session_state.predictions[rank][0])/abs(st.session_state.predictions[rank][0])*100)+"%")
    
    # if stock, show description
    if st.session_state.stocks[rank][1].asset_type == "Stock":
        with st.expander("Stock Description"):
            # st.write(stock_model(st.session_state.stocks[rank][1].ticker))
            st.write("")

    with st.expander("Further information"):
        st.write(st.session_state.stocks[rank][1])

def PrintUser():
    # income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level
    user = st.session_state.user_input
    with st.expander("Your information"):
        st.write(f"Income: ${user[0]}")
        st.write(f"Savings: ${user[1]}")
        st.write(f"Debt to Income Ratio: ${user[2]}")
        st.write(f"Desired Investment Duration: ${user[3]}")
        st.write(f"Monthly Investment Commitment: ${user[4]}")
        st.write(f"Target Return Expectation: ${user[5]}")
        st.write(f"Risk Appetite: ${user[6]}")
        st.write(f"Maximum Drawdown level: ${user[7]}")
        st.write(f"Confidence Level in Investing: ${user[8]}")

if 'user_input' not in st.session_state or DataValidation() != None:
    st.write("Please head back to Start page to let us know your investment preferences!")
    if st.button("Take me back!"):
        st.switch_page("Start.py")
else:
    if (st.session_state.name != ""):
        st.title("Hi, " + st.session_state.name + "!")
    else:
        st.title("Hi!")
    PrintUser()
    st.title("Now, here's your top 3 stocks.")
    GetStocks()
    ShowStock(0)
    ShowStock(1)
    ShowStock(2)
    
    
    # while st.session_state.isLoading:
    #     st.spinner(text="Generating Report...")
    #     if st.session_state.reportReady:
    #         st.session_state.isLoading = False
            
