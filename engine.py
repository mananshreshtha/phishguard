import re

def check_rules(user_input):
    risk_score = 0
    reasons_list = []
    text_lower = user_input.lower()
    
    # 1. Critical Threat: Raw IP Address Check
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    if re.search(ip_pattern, user_input):
        risk_score += 65
        reasons_list.append("Critical threat: Link uses a raw IP address instead of a domain name.")
        
    # 2. Insecure Protocol Check
    if "http://" in text_lower:
        risk_score += 10
        reasons_list.append("Insecure protocol: Link uses unencrypted HTTP instead of HTTPS.")
        
    # 3. Non-Standard Port Check (:8080, etc.)
    if re.search(r':\d{4,5}', user_input):
        risk_score += 15
        reasons_list.append("Suspicious non-standard web port detected.")
        
    # 4. Suspicious Domain Extensions Check (.zip, .click, etc.)
    suspicious_exts = ['.zip', '.click', '.xyz', '.top', '.tk', '.cc', '.link', '.work', '.online']
    found_exts = [ext for ext in suspicious_exts if ext in text_lower]
    if found_exts:
        risk_score += 40
        reasons_list.append(f"Suspicious high-risk domain extension detected: {', '.join(found_exts)}")
        
    # 5. Brand Impersonation Check (sbi, indiapost, hdfc, etc.)
    brands = ['sbi', 'indiapost', 'hdfc', 'icici', 'paytm', 'rbi']
    official_domains = ['sbi.co.in', 'indiapost.gov.in', 'hdfcbank.com']
    found_brands = [b for b in brands if b in text_lower]
    if found_brands and not any(od in text_lower for od in official_domains):
        risk_score += 40
        reasons_list.append(f"Brand impersonation detected for: {', '.join(found_brands).upper()}")
        
    # 6. Urgent Scam & Authentication Keywords
    keywords = ['kyc', 'account suspended', 'otp', 'winner', 'urgent', 'verify', 'download', 'customs', 'auth', 'oauth', 'callback']
    found_keywords = [kw for kw in keywords if kw in text_lower]
    if found_keywords:
        risk_score += 15
        reasons_list.append(f"Suspicious auth/scam keywords found: {', '.join(found_keywords)}")
        
    risk_score = min(risk_score, 100)
    return risk_score, reasons_list

def analyze_input(user_input):
    return check_rules(user_input)
