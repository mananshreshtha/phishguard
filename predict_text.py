import joblib

# 1. Model aur Vectorizer load karna
try:
    model = joblib.load('spam_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
except Exception as e:
    print(f"Error loading model files: {e}")

def predict_text_score(text):
    """
    Text ki spam probability nikal kar use 0-30 scale par weight karta hai.
    """
    try:
        vec_text = vectorizer.transform([text])
        proba = model.predict_proba(vec_text)[0][1]
        
        # Probability ko 0-30 points mein scale karna
        ml_score = round(proba * 30)
        
        if proba > 0.6:
            reason = f"AI Text Model flagged phishing patterns ({int(proba * 100)}% confidence)."
        elif proba >= 0.2:
            reason = f"AI Text Model noticed suspicious keywords ({int(proba * 100)}% confidence)."
        else:
            reason = f"AI Text Model verified text as normal/safe."
            
        return ml_score, reason
        
    except Exception as e:
        return 0, f"Prediction error: {str(e)}"

# 2. Test Cases (False Positive & Phishing Check)
if __name__ == "__main__":
    tests = [
        "Hey, are we meeting today?",
        "Free entry! Win a prize, text WIN to 80086"
    ]
    
    for msg in tests:
        score, reason = predict_text_score(msg)
        print(f"\nMessage: {msg}")
        print(f"Risk Score: {score}/30")
        print(f"Reason: {reason}")