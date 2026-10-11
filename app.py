import streamlit as st
import engine

st.set_page_config(page_title="PhishGuard 🛡️", page_icon="🛡️", layout="centered")

# Custom Styling with Extra Large Input Label
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    div[data-testid="stCaptionContainer"] p {
        font-size: 1.2rem !important;
        color: #c9d1d9 !important;
        font-weight: 500;
    }
    /* Extra Large & Bold Input Label */
    .stTextArea label p {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        font-size: 1.1rem !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #d32f2f 0%, #ff4b4b 100%);
    }
    </style>
""", unsafe_allow_html=True)

# 6 Languages Dictionary
LANG = {
    "English": {
        "title": "PhishGuard 🛡️",
        "caption": "Hybrid AI & Rule-Based Phishing Threat Detection Engine",
        "input_label": "Paste suspicious link or SMS text here:",
        "placeholder": "e.g., Your account has been suspended. Click http://192.168.1.1/login to update KYC.",
        "btn": "Analyze Threat 🚀",
        "spinner": "Scanning message across Rule Engine, ML Model, and Security APIs...",
        "score_label": "Threat Score:",
        "high_risk": "🛑 HIGH RISK: Potential scam or phishing attempt! Do not click or share info.",
        "mod_risk": "⚠️ MODERATE RISK: Proceed with caution. Verify before trusting.",
        "low_risk": "✅ LOW RISK: Message appears safe.",
        "reasons_title": "Detection Reasons:",
        "no_input": "Please paste a text or URL above to analyze."
    },
    "हिन्दी (Hindi)": {
        "title": "PhishGuard 🛡️",
        "caption": "फ़िशिंग और ऑनलाइन घोटालों से बचने का सुरक्षा टूल",
        "input_label": "यहाँ संदिग्ध लिंक या SMS टेक्स्ट पेस्ट करें:",
        "placeholder": "उदा., आपका खाता ब्लॉक है। KYC अपडेट करने के लिए http://... पर क्लिक करें।",
        "btn": "खतरे की जाँच करें 🚀",
        "spinner": "संदेश की जाँच की जा रही है...",
        "score_label": "खतरे का स्कोर (Threat Score):",
        "high_risk": "🛑 अत्यधिक खतरा: यह एक स्कैम हो सकता है! इस पर क्लिक न करें।",
        "mod_risk": "⚠️ मध्यम खतरा: सावधानी बरतें, पूरी तरह जाँच लें।",
        "low_risk": "✅ सुरक्षित: संदेश सामान्य और सुरक्षित लग रहा है।",
        "reasons_title": "पहचान के कारण:",
        "no_input": "कृपया जाँच के लिए ऊपर दिए गए बॉक्स में टेक्स्ट या लिंक डालें।"
    },
    "বাংলা (Bengali)": {
        "title": "PhishGuard 🛡️",
        "caption": "হাইব্রিড এআই এবং রুল-ভিত্তিক ফিশিং থ্রেট ডিটেকশন ইঞ্জিন",
        "input_label": "এখানে সন্দেহজনক লিঙ্ক বা এসএমএস টেক্সট পেস্ট করুন:",
        "placeholder": "যেমন, আপনার অ্যাকাউন্ট স্থগিত করা হয়েছে। KYC আপডেট করতে http://... এ ক্লিক করুন।",
        "btn": "ঝুঁকি বিশ্লেষণ করুন 🚀",
        "spinner": "বার্তা স্ক্যান করা হচ্ছে...",
        "score_label": "থ্রেট স্কোর:",
        "high_risk": "🛑 উচ্চ ঝুঁকি: সম্ভাব্য স্ক্যাম বা ফিশিং প্রচেষ্টা! ক্লিক বা তথ্য শেয়ার করবেন না।",
        "mod_risk": "⚠️ মাঝারি ঝুঁকি: সতর্কতার সাথে এগিয়ে যান।",
        "low_risk": "✅ কম ঝুঁকি: বার্তাটি নিরাপদ মনে হচ্ছে।",
        "reasons_title": "সনাক্তকরণের কারণ:",
        "no_input": "বিশ্লেষণ করতে অনুগ্রহ করে উপরে একটি টেক্সট বা URL পেস্ট করুন।"
    },
    "मराठी (Marathi)": {
        "title": "PhishGuard 🛡️",
        "caption": "हायब्रिड AI आणि नियम-आधारित फिशिंग थ्रेट डिटेक्शन इंजिन",
        "input_label": "येथे संशयास्पद दुवा किंवा SMS मजकूर पेस्ट करा:",
        "placeholder": "उदा., तुमचे खाते निलंबित केले आहे. KYC अद्यतनित करण्यासाठी http://... वर क्लिक करा.",
        "btn": "धोका तपासा 🚀",
        "spinner": "संदेश स्कॅन करत आहे...",
        "score_label": "धोक्याचा स्कोअर:",
        "high_risk": "🛑 उच्च धोका: संभाव्य स्कैम किंवा फिशिंग प्रयत्न! क्लिक करू नका.",
        "mod_risk": "⚠️ मध्यम धोका: काळजीपूर्वक पुढे जा.",
        "low_risk": "✅ कमी धोका: संदेश सुरक्षित दिसत आहे.",
        "reasons_title": "ओळखण्याची कारणे:",
        "no_input": "कृपया विश्लेषणासाठी वर मजकूर किंवा URL पेस्ट करा."
    },
    "తెలుగు (Telugu)": {
        "title": "PhishGuard 🛡️",
        "caption": "హైబ్రిడ్ AI & రూల్-బేస్డ్ ఫిషింగ్ త్రెట్ డిటెక్షన్ ఇంజిన్",
        "input_label": "అనుమానాస్పద లింక్ లేదా SMS టెక్స్ట్‌ని ఇక్కడ పేస్ట్ చేయండి:",
        "placeholder": "ఉదా., మీ ఖాతా సస్పెండ్ చేయబడింది. KYC అప్‌డేట్ చేయడానికి http://... క్లిక్ చేయండి.",
        "btn": "ప్రమాదాన్ని విశ్లేషించండి 🚀",
        "spinner": "సందేశాన్ని స్కాన్ చేస్తోంది...",
        "score_label": "త్రెట్ స్కోర్:",
        "high_risk": "🛑 అత్యధిక ప్రమాదం: సంభావ్య మోసం లేదా ఫిషింగ్ ప్రయత్నం! క్లిక్ చేయవద్దు.",
        "mod_risk": "⚠️ మధ్యస్థ ప్రమాదం: జాగ్రత్తగా వ్యవహరించండి.",
        "low_risk": "✅ తక్కువ ప్రమాదం: సందేశం సురక్షితంగా కనిపిస్తోంది.",
        "reasons_title": "గుర్తించడానికి కారణాలు:",
        "no_input": "దయచేసి విశ్లేషించడానికి పైన టెక్స్ట్ లేదా URLని పేస్ట్ చేయండి."
    },
    "தமிழ் (Tamil)": {
        "title": "PhishGuard 🛡️",
        "caption": "ஹைப்ரிட் AI & விதி-அடிப்படையிலான ஃபிஷிங் அச்சுறுத்தல் கண்டறிதல் இயந்திரம்",
        "input_label": "சந்தேகத்திற்கிடமான இணைப்பு அல்லது SMS உரையை இங்கே ஒட்டவும்:",
        "placeholder": "எ.கா., உங்கள் கணக்கு முடக்கப்பட்டுள்ளது. KYC ஐப் புதுப்பிக்க http://... ஐக் கிளிக் செய்யவும்.",
        "btn": "அச்சுறுத்தலைப் பகுப்பாய்வு செய் 🚀",
        "spinner": "செய்தி ஸ்கேன் செய்யப்படுகிறது...",
        "score_label": "அச்சுறுத்தல் மதிப்பெண்:",
        "high_risk": "🛑 அதிக ஆபத்து: சாத்தியமான மோசடி அல்லது ஃபிஷிங் முயற்சி! கிளிக் செய்ய வேண்டாம்.",
        "mod_risk": "⚠️ மிதமான ஆபத்து: எச்சரிக்கையுடன் தொடரவும்.",
        "low_risk": "✅ குறைந்த ஆபத்து: செய்தி பாதுகாப்பாகத் தெரிகிறது.",
        "reasons_title": "கண்டறிதல் காரணங்கள்:",
        "no_input": "பகுப்பாய்வு செய்ய மேலே உரை அல்லது URL ஐ ஒட்டவும்."
    }
}

# Localization helper function for detection reasons
def get_localized_reason(reason, lang):
    translations = {
        "हिन्दी (Hindi)": {
            "Critical threat: Link contains a raw IP address instead of a domain.": "गंभीर खतरा: लिंक में डोमेन के बजाय सीधे IP एड्रेस का उपयोग किया गया है।",
            "URL shortener detected (commonly used to hide malicious links).": "URL शॉर्टनर का पता चला (आमतौर पर खतरनाक लिंक छिपाने के लिए उपयोग किया जाता है)।",
            "Suspicious domain extension detected.": "संदिग्ध डोमेन एक्सटेंशन का पता चला।",
            "AI Text Model verified text as normal/safe.": "AI टेक्स्ट मॉडल ने टेक्स्ट को सामान्य/सुरक्षित सत्यापित किया।"
        },
        "বাংলা (Bengali)": {
            "Critical threat: Link contains a raw IP address instead of a domain.": "গুরুতর হুমকি: লিঙ্কে ডোমেনের পরিবর্তে সরাসরি IP ঠিকানা রয়েছে।",
            "URL shortener detected (commonly used to hide malicious links).": "ইউআরএল শর্টনার সনাক্ত করা হয়েছে (সাধারণত ক্ষতিকারক লিঙ্ক লুকাতে ব্যবহৃত হয়)।",
            "Suspicious domain extension detected.": "সন্দেহজনক ডোমেন এক্সটেনশন সনাক্ত করা হয়েছে।",
            "AI Text Model verified text as normal/safe.": "AI টেক্সট মডেল পাঠ্যটিকে স্বাভাবিক/নিরাপদ বলে যাচাই করেছে।"
        },
        "मराठी (Marathi)": {
            "Critical threat: Link contains a raw IP address instead of a domain.": "गंभीर धोका: दुव्यामध्ये डोमेनऐवजी थेट IP पत्ता आहे.",
            "URL shortener detected (commonly used to hide malicious links).": "URL शॉर्टर आढळले (सामान्यत: घातक दुवे लपवण्यासाठी वापरले जाते).",
            "Suspicious domain extension detected.": "संशयास्पद डोमेन विस्तार आढळला.",
            "AI Text Model verified text as normal/safe.": "AI टेक्स्ट मॉडेलने मजकूर सामान्य/सुरक्षित म्हणून सत्यापित केला."
        },
        "తెలుగు (Telugu)": {
            "Critical threat: Link contains a raw IP address instead of a domain.": "తీవ్రమైన ప్రమాదం: లింక్‌లో డొమైన్‌కి బదులుగా నేరుగా IP చిరునామా ఉంది.",
            "URL shortener detected (commonly used to hide malicious links).": "URL షార్ట్‌నర్ కనుగొనబడింది (సాధారణంగా హానికరమైన లింక్‌లను దాచడానికి ఉపయోగిస్తారు).",
            "Suspicious domain extension detected.": "అనుమానాస్పద డొమైన్ పొడిగింపు కనుగొనబడింది.",
            "AI Text Model verified text as normal/safe.": "AI టెక్స్ట్ మోడల్ టెక్స్ట్‌ని సాధారణమైనదిగా/సురక్షితమైనదిగా ధృవీకరించింది."
        },
        "தமிழ் (Tamil)": {
            "Critical threat: Link contains a raw IP address instead of a domain.": "கடுமையான அச்சுறுத்தல்: இணைப்பில் டொமைனுக்குப் பதிலாக நேரடி IP முகவரி உள்ளது.",
            "URL shortener detected (commonly used to hide malicious links).": "URL சுருக்கி கண்டறியப்பட்டது (பொதுவாக தீங்கிழைக்கும் இணைப்புகளை மறைக்கப் பயன்படுகிறது).",
            "Suspicious domain extension detected.": "சந்தேகத்திற்கிடமான டொமைன் நீட்டிப்பு கண்டறியப்பட்டது.",
            "AI Text Model verified text as normal/safe.": "AI உரை மாதிரி உரையை சாதாரணமானது/பாதுகாப்பானது என சரிபார்த்தது."
        }
    }
    
    if lang in translations and reason in translations[lang]:
        return translations[lang][reason]
        
    # Handle dynamic keyword strings
    if "High-risk scam/urgency keywords found:" in reason:
        keywords_part = reason.split(":")[-1]
        prefixes = {
            "हिन्दी (Hindi)": "उच्च जोखिम वाले घोटाले/तत्काल कीवर्ड मिले:",
            "বাংলা (Bengali)": "উচ্চ ঝুঁকিপূর্ণ স্ক্যাম/জরুরী কীওয়ার্ড পাওয়া গেছে:",
            "मराठी (Marathi)": "उच्च जोखमीचे घोटाळा/तातडीचे कीवर्ड आढळले:",
            "తెలుగు (Telugu)": "అధిక ప్రమాదం గల స్కామ్/అత్యవసర కీవర్డ్‌లు కనుగొనబడ్డాయి:",
            "தமிழ் (Tamil)": "அதிக ஆபத்துள்ள மோசடி/அவசர முக்கிய வார்த்தைகள் கண்டறியப்பட்டன:"
        }
        if lang in prefixes:
            return f"{prefixes[lang]} {keywords_part}"
            
    # Handle AI confidence model strings
    if "AI Text Model flagged phishing patterns" in reason:
        ai_prefixes = {
            "हिन्दी (Hindi)": "AI टेक्स्ट मॉडल ने फ़िशिंग पैटर्न का पता लगाया है",
            "বাংলা (Bengali)": "AI টেক্সট মডেল ফিশিং প্যাটার্ন চিহ্নিত করেছে",
            "मराठी (Marathi)": "AI टेक्स्ट मॉडेलने फिशिंग पॅटर्न ओळखले आहेत",
            "తెలుగు (Telugu)": "AI టెక్స్ట్ మోడల్ ఫిషింగ్ నమూనాలను గుర్తించింది",
            "தமிழ் (Tamil)": "AI உரை மாதிரி ஃபிஷிங் வடிவங்களைக் கண்டறிந்துள்ளது"
        }
        if lang in ai_prefixes:
            suffix = reason[reason.find("("):] if "(" in reason else ""
            return f"{ai_prefixes[lang]} {suffix}"
            
    return reason

# Sidebar Greetings Header
st.sidebar.title("🌐🗣️ Hi / नमस्ते / নমস্কার / नमस्कार / నమస్కారం / வணக்கம்")
selected_lang_name = st.sidebar.selectbox("Select Language", list(LANG.keys()))
t = LANG[selected_lang_name]

# Render UI Elements
st.title(t["title"])
st.caption(t["caption"])
st.markdown("---")

user_input = st.text_area(t["input_label"], height=120, placeholder=t["placeholder"])

if st.button(t["btn"], use_container_width=True):
    if user_input.strip():
        with st.spinner(t["spinner"]):
            score, reasons = engine.analyze_input(user_input)
            
        st.markdown("---")
        st.subheader(f"{t['score_label']} {score} / 100")
        
        if score >= 60:
            st.error(t["high_risk"])
        elif score >= 25:
            st.warning(t["mod_risk"])
        else:
            st.success(t["low_risk"])
            
        st.write(f"### {t['reasons_title']}")
        for reason in reasons:
            localized_reason = get_localized_reason(reason, selected_lang_name)
            st.write(f"- {localized_reason}")
    else:
        st.info(t["no_input"])