from rules import check_rules
from predict_text import predict_text_score

def analyze_input(user_input):
    """
    Combines rule-based checks and machine learning predictions 
    to calculate a final threat score and aggregate all reasons.
    """
    # 1. Get score and reasons from Harshit's rule engine
    rule_score, rule_reasons = check_rules(user_input)
    
    # 2. Get score and reason from Vishal's ML prediction model
    ml_score, ml_reason = predict_text_score(user_input)
    
    # 3. Combine scores together
    total_score = rule_score + ml_score
    
    # 4. Combine all reasons into a single list
    all_reasons = rule_reasons.copy()
    if ml_reason:
        all_reasons.append(ml_reason)
        
    return total_score, all_reasons