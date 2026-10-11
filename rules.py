# Title: Rule-Based Threat & Scam Detection Engine

import re

def check_rules(user_input):
    """
    Scans user text/link with higher weights for critical threats 
    to properly flag severe phishing attempts.
    """
    risk_score = 0
    reasons_list = []
    
    text_lower = user_input.lower()
    
    # 1. IP Address Check (Very high risk in URLs)
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    if re.search(ip_pattern, user_input):
        risk_score += 35  # Increased weight
        reasons_list.append("Critical threat: Link contains a raw IP address instead of a domain.")
        
    # 2. URL Shortener Check
    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl']
    if any(shortener in text_lower for shortener in shorteners):
        risk_score += 25
        reasons_list.append("URL shortener detected (commonly used to hide malicious links).")
        
    # 3. Suspicious Domain Extensions Check
    suspicious_exts = ['.xyz', '.top', '.tk', '.cc']
    if any(ext in text_lower for ext in suspicious_exts):
        risk_score += 25
        reasons_list.append("Suspicious domain extension detected.")
        
    # 4. Urgent Scam Keywords Check ("KYC", "account suspended", etc.)
    keywords = ['kyc', 'account suspended', 'otp', 'winner', 'lottery', 'urgent', 'suspended']
    found_keywords = [kw for kw in keywords if kw in text_lower]
    
    if found_keywords:
        risk_score += 30  # Increased weight for social engineering keywords
        reasons_list.append(f"High-risk scam/urgency keywords found: {', '.join(found_keywords)}")
        
    return risk_score, reasons_list