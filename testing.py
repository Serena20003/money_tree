import unittest
import algorithm
import database

class TestCalculateRiskLevel(unittest.TestCase):
    def test_calculate_risk_level_base(self):
        low_risk = algorithm.calculate_risk_level(10, 2, -10)
        high_risk = algorithm.calculate_risk_level(50, 1, -50)
        self.assertGreater(high_risk, low_risk)
    def test_calculate_risk_level_beta1(self):
        low_risk = algorithm.calculate_risk_level(10, 2, -10)
        high_risk = algorithm.calculate_risk_level(10, 1, -10)
        self.assertGreater(high_risk, low_risk)
    def test_calculate_risk_level_beta2(self):
        low_risk = algorithm.calculate_risk_level(10, 1, -10)
        high_risk = algorithm.calculate_risk_level(10, 0, -10)
        self.assertGreater(high_risk, low_risk)
    def test_calculate_risk_level_beta3(self):
        low_risk = algorithm.calculate_risk_level(10, 2, -10)
        high_risk = algorithm.calculate_risk_level(10, 0, -10)
        self.assertGreater(high_risk, low_risk)
    def test_calculate_risk_level_appetite1(self):
        low_risk = algorithm.calculate_risk_level(10, 1, -10)
        high_risk = algorithm.calculate_risk_level(11, 1, -10)
        self.assertGreater(high_risk, low_risk)
    def test_calculate_risk_level_appetite2(self):
        low_risk = algorithm.calculate_risk_level(5, 1, -10)
        high_risk = algorithm.calculate_risk_level(100, 2, -10)
        self.assertGreater(high_risk, low_risk)

class TestCompatability(unittest.TestCase):
    def test_compatability_volatility(self):
        income = 1000000
        savings = 3000
        ratio = 0.113
        duration = 1
        commitment = 3000
        target = 0.7
        appetite = 50
        max_drawdown = 50
        skill_level = "intermediate"
        information = [income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level]
        user = database.User()
        user.parse_information_tester(information)

        volatility = 0.5202341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score1 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score1 = algorithm.calculate_compatability(user, risk_score1, drawdown, min_investment)

        volatility = 0.3202341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score2 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score2 = algorithm.calculate_compatability(user, risk_score2, drawdown, min_investment)
        self.assertGreater(risk_score1, risk_score2)
        self.assertGreater(score1, score2)
    
    def test_compatability_volatility_low_appetite(self):
        income = 1000000
        savings = 3000
        ratio = 0.113
        duration = 1
        commitment = 3000
        target = 0.7
        appetite = 10
        max_drawdown = 10
        skill_level = "intermediate"
        information = [income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level]
        user = database.User()
        user.parse_information_tester(information)

        volatility = 0.5202341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score1 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score1 = algorithm.calculate_compatability(user, risk_score1, drawdown, min_investment)

        volatility = 0.0902341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score2 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score2 = algorithm.calculate_compatability(user, risk_score2, drawdown, min_investment)
        self.assertGreater(risk_score1, risk_score2)
        self.assertGreater(score2, score1)

    def test_compatability_volatility_high_appetite(self):
        income = 1000000
        savings = 3000
        ratio = 0.113
        duration = 1
        commitment = 3000
        target = 0.7
        appetite = 100
        max_drawdown = 50
        skill_level = "intermediate"
        information = [income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level]
        user = database.User()
        user.parse_information_tester(information)

        volatility = 0.5202341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score1 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score1 = algorithm.calculate_compatability(user, risk_score1, drawdown, min_investment)

        volatility = 0.3202341964673404
        beta = 1.003
        drawdown = -0.10535004728381722
        min_investment = 0

        risk_score2 = algorithm.calculate_risk_level(volatility, beta, drawdown)
        score2 = algorithm.calculate_compatability(user, risk_score2, drawdown, min_investment)
        self.assertGreater(risk_score1, risk_score2)
        self.assertGreater(score1, score2)

if __name__ == '__main__':
    unittest.main()