import database
import algorithm

def get_user():
    income = 1000000
    savings = input("Savings: ")
    ratio = 0.113
    duration = 1
    commitment = 3000
    target = 0.7
    appetite = input("Risk Appetite: ")
    max_drawdown = input("Max Drawdown Comfort Level: ")
    skill_level = "beginner"
    information = [income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level]
    user = database.User()
    user.parse_information_tester(information)
    return user

def get_investments():
    opportunities = []
    for i in range(10):
        print("Invesment " + str(i + 1))
        name = input("Name: ")
        asset_type = 'stock'
        beta = input("Beta: ")
        volatility = input("Volatility: ")
        drawdown = input("Drawdown: ")
        minimum_duration = input("Minimum Investment Duration: ")
        information = [name, asset_type, beta, volatility, drawdown, minimum_duration]
        opportunities += [database.Investment(information)]
        print()
    return opportunities

def main_inputs():
    user = get_user()
    print()
    opportunities = get_investments()
    print_investors(algorithm.match_investors(user, opportunities))

def print_investors(investors):
    print()
    for i in investors:
        print(i[1].name)


def main():
    user = get_user()
    opportunities = database.get_investments_from_csv()
    
    print_investors(algorithm.match_investors(user, opportunities))


if __name__ == '__main__':
    main()