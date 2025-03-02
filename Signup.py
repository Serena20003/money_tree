import streamlit as st

def Signup():
    user_input = []
    st.markdown("""
        <style>
            .stSlider > div div {
                margin-left: 5px;
                margin-right: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    if st.button("login instead"):
        st.session_state.user_status = 1

    # form
    signup_input_labels = ["What is your annual income?", 
    "What is your savings?",
    "What is your debt-to-income ratio?",
    "What is the desired investment duration?",
    "Please specify the duration",
    "What is your monthly investment commitment?",
    "What is your target return expection (%)?",
    "What is your risk appetite (%)?",
    "What is your maximum drawdown comfort level (%)?",
    "What is your confidence level in stock investing?"
    ]
    signup_input_error = [0,0,0,0,0,0,0,0,0,0]
    with st.form("userInput", enter_to_submit=False):
        st.title("Info to generate a stock rec report:")
        # 0
        income_val = st.number_input(signup_input_labels[0], 0, step=1, value=None)
        if (signup_input_error[0]):
            st.error("Please fill out the above field")
        # 1
        savings_val = st.number_input(signup_input_labels[1], 0, step=1, value=None)
        if (signup_input_error[1]):
            st.error("Please fill out the above field")
        # 2
        ratio_val = st.number_input(signup_input_labels[2], step=0.1, value=None)
        if (signup_input_error[2]):
            st.error("Please fill out the above field")
        # 3
        investment_duration_category = st.selectbox(signup_input_labels[3], ("Short-term (< 1 year)", "Medium-term (1-5 years)", "Long-term (5+ years)"), index=None, placeholder="Please select a duration type"[3])
        investment_duration_val = None
        if (signup_input_error[3]):
            st.error("Please fill out the above field")
        # 4
        if (investment_duration_category == "Short-term (< 1 year)"):
            investment_duration_val = st.number_input(signup_input_labels[4], 1, 11, value=None, help="Please input number of months")
        elif (investment_duration_category == "Medium-term (1-5 years)"):
            investment_duration_val = st.number_input(signup_input_labels[4], 1, 5, value=None, help="Please input number of years")
        elif (investment_duration_category == "Long-term (5+ years)"):
            investment_duration_val = st.number_input(signup_input_labels[4], 6, value=None, help="Please input number of years")
        if (signup_input_error[4]):
            st.error("Please fill out the above field")
        # 5
        monthly_investment_commitment_val = st.number_input(signup_input_labels[5], 0, step=1, value=None)
        if (signup_input_error[5]):
            st.error("Please fill out the above field")
        # 6
        tre_val = st.slider(signup_input_labels[6], 0, 100, value=None)
        if (signup_input_error[6]):
            st.error("Please fill out the above field")
        # 7
        risk_appetite_val = st.slider(signup_input_labels[7], 0, 100, help="0%: extremely conservative, 100%: extremely aggressive", value=None)
        if (signup_input_error[7]):
            st.error("Please fill out the above field")
        # 8
        max_drawdown_comfort_level_val = st.number_input(signup_input_labels[8], 0, 100, value=None)
        if (signup_input_error[8]):
            st.error("Please fill out the above field")
        # 9
        skill_val = st.select_slider(signup_input_labels[9], options=["Beginner", "Intemediate", "Advanced"], value=None)
        if (signup_input_error[9]):
            st.error("Please fill out the above field")
        submitted = st.form_submit_button("Submit")
        if submitted:
            # data validation
            signup_input_error = [0,0,0,0,0,0,0,0,0,0]
            user_input = [income_val, savings_val, ratio_val, investment_duration_category, investment_duration_val, monthly_investment_commitment_val, tre_val, risk_appetite_val, max_drawdown_comfort_level_val, skill_val]
            validation = DataValidation(user_input, signup_input_error)
            st.write(signup_input_error)
            if type(validation == list):
                err_msg = "Not all fields are filled in:"
                for j in validation:
                    err_msg += " " + signup_input_labels[j] + "\n"
                    # div:has(> is only works on relatively new browsers
                    # st.markdown('<style> div:has(> input[aria-label="' + signup_input_labels[j] + '"]) {background-color: #FFB6C1 !important;}</style>', unsafe_allow_html=True)
                st.error(err_msg)
            elif type(validation) == str:
                st.error(validation)
            # send data
            # pg = st.navigation([st.Page("Home.py"), st.Page("Chat.py"), st.Page("Top10.py"), st.Page("Setting.py")])
            # pg.run()

def DataValidation(user_input, signup_input_error):
    # check if all fields are filled out
    fields_wo_val = []
    for i in range(len(user_input)):
        if user_input[i] == None:
            fields_wo_val.append(i)
            signup_input_error[i] = 1
    if len(fields_wo_val) != 0:
        return fields_wo_val
    
Signup()