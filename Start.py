import streamlit as st
import base64

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def Setup():
    bin_str = get_base64("assets/bg.jpg")
    st.markdown("""
        <style>
            .stApp {
                background-image: url("data:image/png;base64,%s");
                background-size: cover;
            }
        </style>
    """ % bin_str, unsafe_allow_html=True)

def DataValidation():
    # check if all fields are filled out
    fields_wo_val = []
    for i in range(len(st.session_state.user_input)):
        if st.session_state.user_input[i] == None:
            fields_wo_val.append(i)
            st.session_state.signup_input_error[i] = 1
    if len(fields_wo_val) != 0:
        return fields_wo_val
    if (st.session_state.user_input[7] == 0):
        return "Risk level cannot be zero!"
    return None
    
def Signup():
    if 'user_input' not in st.session_state:
        st.session_state.user_input = [None] * 9
    if 'name' not in st.session_state:
        st.session_state.name = ""
    st.markdown("""
        <style>
            .stSlider > div div {
                margin-left: 5px;
                margin-right: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # if st.button("login instead"):
    #     st.session_state.user_status = 1

    # form
    signup_input_labels = ["What is your annual income ($)?", 
    "What is your savings ($)?",
    "What is your debt-to-income ratio?",
    "What is the desired investment duration?",
    "What is your monthly investment commitment ($)?",
    "What is your target return expection (%)?",
    "What is your risk appetite (%)?",
    "What is your maximum drawdown comfort level (%)?",
    "What is your confidence level in stock investing?"
    ]
    if 'signup_input_error' not in st.session_state:
        st.session_state.signup_input_error = [0,0,0,0,0,0,0,0,0]
    
    with st.form("userInput"):
        st.session_state.name = st.text_input("What should we call you? (optional)", st.session_state.name)
        # 0
        st.session_state.user_input[0] = st.number_input(signup_input_labels[0], 0, step=1, value=st.session_state.user_input[0])
        if (st.session_state.signup_input_error[0]):
            st.error("Please fill out the above field")
        # 1
        st.session_state.user_input[1] = st.number_input(signup_input_labels[1], 0, step=1, value=st.session_state.user_input[1])
        if (st.session_state.signup_input_error[1]):
            st.error("Please fill out the above field")
        # 2
        st.session_state.user_input[2] = st.number_input(signup_input_labels[2], step=0.1, value=st.session_state.user_input[2])
        if (st.session_state.signup_input_error[2]):
            st.error("Please fill out the above field")
        # 3
        st.session_state.user_input[3] = st.select_slider(signup_input_labels[3], options=["Short-term (< 1 year)", "Medium-term (1-5 years)", "Long-term (5+ years)"], value=st.session_state.user_input[3])
        if (st.session_state.signup_input_error[3]):
            st.error("Please fill out the above field")
        # 4
        st.session_state.user_input[4] = st.number_input(signup_input_labels[4], 0, step=1, value=st.session_state.user_input[4])
        if (st.session_state.signup_input_error[4]):
            st.error("Please fill out the above field")
        # 5
        st.session_state.user_input[5] = st.number_input(signup_input_labels[5], 0, 100, value=st.session_state.user_input[5])
        if (st.session_state.signup_input_error[5]):
            st.error("Please fill out the above field")
        # 6
        st.session_state.user_input[6] = st.slider(signup_input_labels[6], 0, 100, help="0%: extremely conservative, 100%: extremely aggressive", value=st.session_state.user_input[6])
        if (st.session_state.signup_input_error[6]):
            st.error("Please fill out the above field")
        # 7
        st.session_state.user_input[7] = st.number_input(signup_input_labels[7], 0, 100, value=st.session_state.user_input[7])
        if (st.session_state.signup_input_error[7]):
            st.error("Please fill out the above field")
        # 8
        st.session_state.user_input[8] = st.select_slider(signup_input_labels[8], options=["Beginner", "Intemediate", "Advanced"], value=st.session_state.user_input[8])
        if (st.session_state.signup_input_error[8]):
            st.error("Please fill out the above field")
        submitted = st.form_submit_button("Submit")
        if submitted:
            # data validation
            st.session_state.persistData = False
            st.session_state.signup_input_error = [0,0,0,0,0,0,0,0,0]
            # st.session_state.user_input = [income_val, savings_val, ratio_val, st.session_state.investment_duration_category, investment_duration_val, monthly_investment_commitment_val, tre_val, risk_appetite_val, max_drawdown_comfort_level_val, skill_val]
            validation = DataValidation()
            if (validation == None):
                st.switch_page("pages/Report.py")
            elif type(validation)  == list:
                err_msg = "Not all fields are filled in:"
                for j in validation:
                    err_msg += " " + signup_input_labels[j]
                    # div:has(> is only works on relatively new browsers
                    # st.markdown('<style> div:has(> input[aria-label="' + signup_input_labels[j] + '"]) {background-color: #FFB6C1 !important;}</style>', unsafe_allow_html=True)
                st.error(err_msg)
            elif type(validation) == str:
                st.error(validation)
            # st.switch_page("Start.py")
            # pg = st.navigation([st.Page("Home.py"), st.Page("Chat.py"), st.Page("Top10.py"), st.Page("Setting.py")])
            # pg.run()

Setup()
st.title("Hi, let's kick start your investment journey!")
# if st.button("Reset Form", type="secondary"):
#     st.session_state.user_input = [None] * 9
#     st.session_state.name = ""
Signup()
