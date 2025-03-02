import database
import math

EXPERIENCE_CATEGORIES = {
    "beginner": {"ETF", "Index Fund", "Blue-Chip", "Government Bond"},
    "intermediate": {"Growth", "REIT", "BOND", "Dividend Aristocrat"},
    "advanced": {"Crypto", "Commodities"}
}

def calculate_risk_level(volatility, beta, drawdown):
    # Assign weights to each factor to calculate risk
    volatility_weight = 0.6
    beta_weight = 0.2
    drawdown_weight = 0.2
    if beta > 0:
        beta = -min(abs(beta), 100)
    else:
        beta = min(abs(beta), 100)
    # Risk score calculation (higher volatility, higher beta, and more negative drawdown increase risk)
    risk_score = (volatility * volatility_weight) + (beta * beta_weight) + (abs(drawdown) * drawdown_weight)
    
    return risk_score

def calculate_compatability(user, investment_risk_score, investment_drawdown, min_investment):
    drawdown_diff = abs(user.max_drawdown - investment_drawdown)
    drawdown_compatibility = max(0, 1 - (drawdown_diff / user.max_drawdown))
    if investment_risk_score*100 > user.appetite:
        risk_compatibility = 0
    else:
        risk_compatibility = max(0, ((investment_risk_score*100) / user.appetite if user.appetite != 0 else 0))
    print(investment_risk_score*100, user.appetite, risk_compatibility)
    if min_investment:
        investment_compatibility = max(0, 1 - (min_investment / user.savings))
        compatibility_score = (0.3*drawdown_compatibility + 0.3*risk_compatibility + 0.4*investment_compatibility)
    else:
        compatibility_score = (0.5*drawdown_compatibility + 0.5*risk_compatibility)
    return compatibility_score

def match_investors(user, opportunities):
    investments = []
    experience_levels = ["beginner", "intermediate", "advanced"]
    user_level = user.skill_level.lower()
    allowed_categories = set()
    for level in experience_levels:
        allowed_categories.update(EXPERIENCE_CATEGORIES[level])
        if level == user_level:  # Stop when we reach the user's level
            break
    print(allowed_categories)
    for investment in opportunities:
        if (investment.category not in allowed_categories) and (investment.asset_type not in allowed_categories):
            continue
        if investment.min_investment > user.savings * user.commitment:
            continue
        investment.risk_score = calculate_risk_level(investment.volatility, investment.beta, investment.drawdown)
        score = calculate_compatability(user, investment.risk_score, investment.drawdown, investment.min_investment)
        if score < 0:
            continue
        investments += [(score, investment)]
    investments = [(score, investment) for score, investment in investments if not math.isnan(score)]
    investments.sort(key=lambda x: x[0], reverse=True)
    return investments[:3]