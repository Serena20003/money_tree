import pandas as pd

class User:

    def __init__(self):
        self.income = int
        self.savings = int
        self.ratio = int
        self.duration = int
        self.commitment = int
        self.target = int
        self.appetite = int
        self.max_drawdown = float
        self.skill_level = ""

    def print_elems_tester(self):
        print(self.income, self.savings, self.ratio, self.goals, self.duration, self.commitment, 
        self.target, self.appetite, self.max_drawdown, self.skill_level)

    def parse_information_tester(self, information):
        self.income = int(information[0])
        self.savings = int(information[1])
        self.ratio = int(information[2])
        self.duration = int(information[3])
        self.commitment = int(information[4])
        self.target = int(information[5])
        self.appetite = int(information[6])
        self.max_drawdown = float(information[7])
        self.skill_level = information[8]

class Investment:
    def __init__(self, row):
        self.ticker = row['Ticker']
        self.name = row['Name']
        self.gics_sector = row['GICS Sector']
        self.category = row['Category']
        self.asset_type = row['Asset Type']
        self.sector = row['Sector']
        self.min_investment = row['Min Investment']
        self.yield_percentage = row['Yield (%)']
        self.expense_ratio = row['Expense Ratio']
        self.price = row['Price']
        self.volatility = row['Volatility']
        self.beta = row['Beta']
        self.drawdown = row['Historical Drawdown']
        self.duration = 1
        self.risk_score = None

def get_investments_from_csv():
    try:
        df = pd.read_csv("combined_financial_data.csv")
        opportunities = [Investment(row) for _, row in df.iterrows()]
        return opportunities
    except FileNotFoundError:
        print(f"Error: File not found.")
        return []