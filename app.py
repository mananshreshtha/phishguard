import cv2
import numpy as np
from PIL import Image
import streamlit as st
import engine

# Optional pyzbar import for advanced robust QR code detection
try:
  from pyzbar import pyzbar

  PYZBAR_AVAILABLE = True
except ImportError:
  PYZBAR_AVAILABLE = False

st.set_page_config(
    page_title="PhishGuard 🛡️", page_icon="🛡️", layout="centered"
)

# Custom Styling
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# 6 Languages Dictionary with QR Scanner Localization
LANG = {
    "English": {
        "title": "PhishGuard 🛡️",
        "caption": (
            "Hybrid AI & Rule-Based Phishing Threat Detection Engine"
        ),
        "qr_section": "📷 Scan QR Code / Screenshot (Quishing Protection)",
        "qr_upload": "Upload a QR Code or Screenshot:",
        "qr_success": "🔗 Extracted Link from QR Code:",
        "qr_fail": (
            "No clear QR code detected in this image. Try uploading a clearer"
            " screenshot or image."
        ),
        "input_label": "Paste suspicious link or SMS text here:",
        "placeholder": (
            "e.g., Your account has been suspended. Click"
            " http://192.168.1.1/login to update KYC."
        ),
        "btn": "Analyze Threat 🚀",
        "spinner": (
            "Scanning message across Rule Engine, ML Model, and Security"
            " APIs..."
        ),
        "score_label": "Threat Score:",
        "high_risk": (
            "🛑 HIGH RISK: Potential scam or phishing attempt! Do not click or"
            " share info."
        ),
        "mod_risk": (
            "⚠️ MODERATE RISK: Proceed with caution. Verify before trusting."
        ),
        "low_risk": "✅ LOW RISK: Message appears safe.",
        "reasons_title": "Detection Reasons:",
        "action_title": "Recommended Action Plan:",
        "no_input": "Please paste a text or URL above to analyze.",
        "actions_high": [
            (
                "🚨 **Do NOT click any links** or enter sensitive information"
                " (passwords, OTPs, UPI PINs)."
            ),
            (
                "📞 **Report Immediately:** Call the **National Cyber Crime"
                " Helpline (1930)** or report at"
                " [cybercrime.gov.in](https://cybercrime.gov.in)."
            ),
            (
                "🔒 **Protect Accounts:** If you entered credentials, change"
                " your passwords immediately and contact your bank to freeze"
                " linked accounts."
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **Verify Before Proceeding:** Contact the official"
                " organization using numbers from their official website, not"
                " from the SMS/link."
            ),
            (
                "🔍 **Inspect the Domain:** Check the sender's email address or"
                " web domain carefully for typos or odd extensions."
            ),
            (
                "🛑 **Avoid Urgent Requests:** Be cautious if the message"
                " pressures you to act quickly."
            ),
        ],
        "actions_low": [
            "✅ **Standard Caution:** No strong phishing indicators detected.",
            (
                "🔒 Always ensure website URLs begin with `https://` before"
                " logging in."
            ),
        ],
    },
    "हिन्दी (Hindi)": {
        "title": "PhishGuard 🛡️",
        "caption": "फ़िशिंग और ऑनलाइन घोटालों से बचने का सुरक्षा टूल",
        "qr_section": "📷 QR कोड / स्क्रीनशॉट स्कैन करें (क्विशिंग सुरक्षा)",
        "qr_upload": "QR कोड या स्क्रीनशॉट अपलोड करें:",
        "qr_success": "🔗 QR कोड से निकाला गया लिंक:",
        "qr_fail": (
            "इस छवि में कोई स्पष्ट QR कोड नहीं मिला। कृपया साफ स्क्रीनशॉट"
            " अपलोड करें।"
        ),
        "input_label": "यहाँ संदिग्ध लिंक या SMS टेक्स्ट पेस्ट करें:",
        "placeholder": (
            "उदा., आपका खाता ब्लॉक है। KYC अपडेट करने के लिए http://... पर क्लिक"
            " करें।"
        ),
        "btn": "खतरे की जाँच करें 🚀",
        "spinner": "संदेश की जाँच की जा रही है...",
        "score_label": "खतरे का स्कोर (Threat Score):",
        "high_risk": (
            "🛑 अत्यधिक खतरा: यह एक स्कैम हो सकता है! इस पर क्लिक न करें।"
        ),
        "mod_risk": "⚠️ मध्यम खतरा: सावधानी बरतें, पूरी तरह जाँच लें।",
        "low_risk": "✅ सुरक्षित: संदेश सामान्य और सुरक्षित लग रहा है।",
        "reasons_title": "पहचान के कारण:",
        "action_title": "अनुशंसित कार्रवाई योजना:",
        "no_input": (
            "कृपया जाँच के लिए ऊपर दिए गए बॉक्स में टेक्स्ट या लिंक डालें।"
        ),
        "actions_high": [
            (
                "🚨 **किसी भी लिंक पर क्लिक न करें** या संवेदनशील जानकारी"
                " (पासवर्ड, OTP, UPI पिन) दर्ज न करें।"
            ),
            (
                "📞 **तुरंत रिपोर्ट करें:** राष्ट्रीय साइबर अपराध हेल्पलाइन"
                " (**1930**) पर कॉल करें या"
                " [cybercrime.gov.in](https://cybercrime.gov.in) पर रिपोर्ट करें।"
            ),
            (
                "🔒 **खातों की सुरक्षा करें:** यदि आपने जानकारी दर्ज कर दी है,"
                " तो तुरंत अपना पासवर्ड बदलें और अपने बैंक से संपर्क करें।"
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **आगे बढ़ने से पहले जाँच करें:** एसएमएस/लिंक में दिए गए"
                " नंबरों के बजाय आधिकारिक वेबसाइट के नंबरों का उपयोग करें।"
            ),
            (
                "🔍 **डोमेन की जाँच करें:** प्रेषक के ईमेल पते या वेब डोमेन की"
                " सावधानीपूर्वक जाँच करें।"
            ),
            (
                "🛑 **तत्काल अनुरोधों से बचें:** यदि संदेश आपको जल्दी कार्रवाई"
                " करने का दबाव डालता है, तो सावधान रहें।"
            ),
        ],
        "actions_low": [
            "✅ **मानक सावधानी:** कोई मजबूत फ़िशिंग संकेत नहीं मिला।",
            (
                "🔒 लॉगिन करने से पहले हमेशा सुनिश्चित करें कि वेबसाइट URL"
                " `https://` से शुरू होता है।"
            ),
        ],
    },
    "বাংলা (Bengali)": {
        "title": "PhishGuard 🛡️",
        "caption": "হাইব্রিড এআই এবং রুল-ভিত্তিক ফিশিং থ্রেট ডিটেকশন ইঞ্জিন",
        "qr_section": "📷 QR কোড / স্ক্রিনশট স্ক্যান করুন (কোয়িশিং সুরক্ষা)",
        "qr_upload": "একটি QR কোড বা স্ক্রিনশট আপলোড করুন:",
        "qr_success": "🔗 QR কোড থেকে এক্সট্রাক্ট করা লিঙ্ক:",
        "qr_fail": (
            "এই ছবিতে কোনো স্পষ্ট QR কোড সনাক্ত করা যায়নি। পরিষ্কার স্ক্রিনশট"
            " আপলোড করুন।"
        ),
        "input_label": "এখানে সন্দেহজনক লিঙ্ক বা এসএমএস টেক্সট পেস্ট করুন:",
        "placeholder": (
            "যেমন, আপনার অ্যাকাউন্ট স্থগিত করা হয়েছে। KYC আপডেট করতে http://..."
            " এ ক্লিক করুন।"
        ),
        "btn": "ঝুঁকি বিশ্লেষণ করুন 🚀",
        "spinner": "বার্তা স্ক্যান করা হচ্ছে...",
        "score_label": "থ্রেট স্কোর:",
        "high_risk": (
            "🛑 উচ্চ ঝুঁকি: সম্ভাব্য স্ক্যাম বা ফিশিং প্রচেষ্টা! ক্লিক বা তথ্য"
            " শেয়ার করবেন না।"
        ),
        "mod_risk": "⚠️ মাঝারি ঝুঁকি: সতর্কতার সাথে এগিয়ে যান।",
        "low_risk": "✅ কম ঝুঁকি: বার্তাটি নিরাপদ মনে হচ্ছে।",
        "reasons_title": "সনাক্তকরণের কারণ:",
        "action_title": "প্রস্তাবিত অ্যাকশন প্ল্যান:",
        "no_input": (
            "বিশ্লেষণ করতে অনুগ্রহ করে উপরে একটি টেক্সট বা URL পেস্ট করুন।"
        ),
        "actions_high": [
            (
                "🚨 **কোনো লিঙ্কে ক্লিক করবেন না** বা সংবেদনশীল তথ্য (পাসওয়ার্ড,"
                " OTP, UPI পিন) প্রবেশ করাবেন না।"
            ),
            (
                "📞 **অবিলম্বে রিপোর্ট করুন:** ন্যাশনাল সাইবার ক্রাইম হেল্পলাইন"
                " (**1930**) নম্বরে কল করুন বা"
                " [cybercrime.gov.in](https://cybercrime.gov.in) এ রিপোর্ট করুন।"
            ),
            (
                "🔒 **অ্যাকাউন্ট সুরক্ষিত করুন:** আপনি তথ্য দিয়ে থাকলে অবিলম্বে"
                " পাসওয়ার্ড পরিবর্তন করুন এবং আপনার ব্যাঙ্কের সাথে যোগাযোগ"
                " করুন।"
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **এগিয়ে যাওয়ার আগে যাচাই করুন:** এসএমএস বা লিঙ্কে থাকা নম্বরের"
                " বদলে অফিশিয়াল ওয়েবসাইটের নম্বর ব্যবহার করুন।"
            ),
            (
                "🔍 **ডোমেন পরীক্ষা করুন:** প্রেরকের ইমেল ঠিকানা বা ওয়েব ডোমেন"
                " সাবধানে চেক করুন।"
            ),
            (
                "🛑 **জরুরি অনুরোধ এড়িয়ে চলুন:** বার্তাটি দ্রুত পদক্ষেপ নেওয়ার"
                " জন্য চাপ সৃষ্টি করলে সতর্ক থাকুন।"
            ),
        ],
        "actions_low": [
            "✅ **সাধারণ সতর্কতা:** কোনো শক্তিশালী ফিশিং লক্ষণ পাওয়া যায়নি।",
            (
                "🔒 লগইন করার আগে সর্বদা নিশ্চিত করুন যে ওয়েবসাইটের URL"
                " `https://` দিয়ে শুরু হচ্ছে।"
            ),
        ],
    },
    "मराठी (Marathi)": {
        "title": "PhishGuard 🛡️",
        "caption": "हायब्रिड AI आणि नियम-आधारित फिशिंग थ्रेट डिटेक्शन इंजिन",
        "qr_section": "📷 QR कोड / स्क्रीनशॉट स्कॅन करा (क्विशिंग सुरक्षा)",
        "qr_upload": "QR कोड किंवा स्क्रीनशॉट अपलोड करा:",
        "qr_success": "🔗 QR कोडमधून काढलेला दुवा:",
        "qr_fail": (
            "या प्रतिमेमध्ये कोणताही स्पष्ट QR कोड आढळला नाही. कृपया स्पष्ट"
            " स्क्रीनशॉट अपलोड करा."
        ),
        "input_label": "येथे संशयास्पद दुवा किंवा SMS मजकूर पेस्ट करा:",
        "placeholder": (
            "उदा., तुमचे खाते निलंबित केले आहे. KYC अद्यतनित करण्यासाठी http://..."
            " वर क्लिक करा."
        ),
        "btn": "धोका तपासा 🚀",
        "spinner": "संदेश स्कॅन करत आहे...",
        "score_label": "धोक्याचा स्कोअर:",
        "high_risk": (
            "🛑 उच्च धोका: संभाव्य स्कैम किंवा फिशिंग प्रयत्न! क्लिक करू नका."
        ),
        "mod_risk": "⚠️ मध्यम धोका: काळजीपूर्वक पुढे जा.",
        "low_risk": "✅ कमी धोका: संदेश सुरक्षित दिसत आहे.",
        "reasons_title": "ओळखण्याची कारणे:",
        "action_title": "शिफारस केलेली कृती योजना:",
        "no_input": "कृपया विश्लेषणासाठी वर मजकूर किंवा URL पेस्ट करा.",
        "actions_high": [
            (
                "🚨 **कोणत्याही दुव्यावर क्लिक करू नका** किंवा संवेदनशील माहिती"
                " (पासवर्ड, OTP, UPI पिन) प्रविष्ट करू नका."
            ),
            (
                "📞 **त्वरित तक्रार करा:** राष्ट्रीय सायबर क्राईम हेल्पलाइन"
                " (**1930**) वर कॉल करा किंवा"
                " [cybercrime.gov.in](https://cybercrime.gov.in) वर तक्रार"
                " नोंदवा."
            ),
            (
                "🔒 **खाती सुरक्षित करा:** तुम्ही माहिती भरली असल्यास, ताबडतोब"
                " पासवर्ड बदला आणि तुमच्या बँकेशी संपर्क साधा."
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **पुढे जाण्यापूर्वी पडताळणी करा:** एसएमएस/लिंकमधील"
                " क्रमांकांऐवजी अधिकृत वेबसाइटवरील क्रमांकांचा वापर करा."
            ),
            (
                "🔍 **डोमेन तपासा:** पाठवणाऱ्याचा ईमेल पत्ता किंवा वेब डोमेन"
                " काळजीपूर्वक तपासा."
            ),
            (
                "🛑 **तातडीच्या विनंती टाळा:** संदेश तुम्हाला त्वरित कृती"
                " करण्यासाठी दबाव टाकत असल्यास सावध राहा."
            ),
        ],
        "actions_low": [
            "✅ **मानक काळजी:** कोणतेही मजबूत फिशिंग संकेत आढळले नाहीत.",
            (
                "🔒 लॉग इन करण्यापूर्वी वेबसाइटचा URL `https://` ने सुरू होतो"
                " याची खात्री करा."
            ),
        ],
    },
    "తెలుగు (Telugu)": {
        "title": "PhishGuard 🛡️",
        "caption": "హైబ్రిడ్ AI & రూల్-బేస్డ్ ఫిషింగ్ త్రెట్ డిటెక్షన్ ఇంజిన్",
        "qr_section": "📷 QR కోడ్ / స్క్రీన్‌షాట్ స్కాన్ చేయండి (క్విషింగ్ భద్రత)",
        "qr_upload": "QR కోడ్ లేదా స్క్రీన్‌షాట్‌ని అప్‌लोड చేయండి:",
        "qr_success": "🔗 QR కోడ్ నుండి సేకరించిన లింక్:",
        "qr_fail": (
            "ఈ చిత్రంలో స్పష్టమైన QR కోడ్ కనుగొనబడలేదు. దయచేసి స్పష్టమైన"
            " స్క్రీన్‌షాట్‌ని అప్‌लोड చేయండి."
        ),
        "input_label": "అనుమానాస్పద లింక్ లేదా SMS టెక్స్ట్‌ని ఇక్కడ పేస్ట్ చేయండి:",
        "placeholder": (
            "ఉదా., మీ ఖాతా సస్పెండ్ చేయబడింది. KYC అప్‌డేట్ చేయడానికి http://..."
            " క్లిక్ చేయండి."
        ),
        "btn": "ప్రమాదాన్ని విశ్లేషించండి 🚀",
        "spinner": "సందేశాన్ని స్కాన్ చేస్తోంది...",
        "score_label": "త్రెట్ స్కోర్:",
        "high_risk": (
            "🛑 అత్యధిక ప్రమాదం: సంభావ్య మోసం లేదా ఫిషింగ్ ప్రయత్నం! క్లిక్"
            " చేయవద్దు."
        ),
        "mod_risk": "⚠️ మధ్యస్థ ప్రమాదం: జాగ్రత్తగా వ్యవహరించండి.",
        "low_risk": "✅ తక్కువ ప్రమాదం: సందేశం సురక్షితంగా కనిపిస్తోంది.",
        "reasons_title": "గుర్తించడానికి కారణాలు:",
        "action_title": "సిఫార్సు చేయబడిన చర్య ప్రణాళిక:",
        "no_input": (
            "దయచేసి విశ్లేషించడానికి పైన టెక్స్ట్ లేదా URLని పేస్ట్ చేయండి."
        ),
        "actions_high": [
            (
                "🚨 **ఏ లింక్పైనా క్లిక్ చేయవద్దు** లేదా సున్నితమైన సమాచారాన్ని"
                " (పాస్‌వర్డ్‌లు, OTPలు, UPI పిన్‌లు) నమోదు చేయవద్దు."
            ),
            (
                "📞 **వెంటనే నివేదించండి:** నేషనల్ సైబర్ క్రైమ్ హెల్ప్‌లైన్"
                " (**1930**)కి కాల్ చేయండి లేదా"
                " [cybercrime.gov.in](https://cybercrime.gov.in)లో నివేదించండి."
            ),
            (
                "🔒 **ఖాతాలను రక్షించండి:** మీరు వివరాలు నమోదు చేసి ఉంటే,"
                " వెంటనే మీ పాస్‌వర్డ్‌ను మార్చండి మరియు మీ బ్యాంకును సంప్రదించండి."
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **ముందుకు వెళ్లే ముందు తనిఖీ చేయండి:** SMS/లింక్‌లోని నంబర్‌ల"
                " కంటే అధికారిక వెబ్‌సైట్ నంబర్‌లను ఉపయోగించండి."
            ),
            (
                "🔍 **డొమైన్‌ను పరిశీలించండి:** పంపినవారి ఈమెయిల్ చిరునామా లేదా"
                " వెబ్ డొమైన్‌ను జాగ్రత్తగా తనిఖీ చేయండి."
            ),
            (
                "🛑 **అత్యవసర అభ్యర్థనలను నివారించండి:** సందేశం మిమ్మల్ని త్వరగా"
                " చర్య తీసుకోవాలని ఒత్తిడి చేస్తే జాగ్రత్తగా ఉండండి."
            ),
        ],
        "actions_low": [
            "✅ **ప్రామాణిక జాగ్రత్త:** బలమైన ఫిషింగ్ సంకేతాలు కనుగొనబడలేదు.",
            (
                "🔒 లాగిన్ చేయడానికి ముందు వెబ్‌సైట్ URL `https://` తో"
                " ప్రారంభమవుతుందని ఎల్లప్పుడూ నిర్ధారించుకోండి."
            ),
        ],
    },
    "தமிழ் (Tamil)": {
        "title": "PhishGuard 🛡️",
        "caption": (
            "ஹைப்ரிட் AI & விதி-அடிப்படையிலான ஃபிஷிங் அச்சுறுத்தல் கண்டறிதல்"
            " இயந்திரம்"
        ),
        "qr_section": "📷 QR குறியீடு / ஸ்கிரீன்ஷாட்டை ஸ்கேன் செய்யவும்",
        "qr_upload": "QR குறியீடு அல்லது ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும்:",
        "qr_success": "🔗 QR குறியீட்டிலிருந்து பிரித்தெடுக்கப்பட்ட இணைப்பு:",
        "qr_fail": (
            "இந்த படத்தில் தெளிவான QR குறியீடு எதுவும் கண்டறியப்படவில்லை."
            " தெளிவான ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும்."
        ),
        "input_label": (
            "சந்தேகத்திற்கிடமான இணைப்பு அல்லது SMS உரையை இங்கே ஒட்டவும்:"
        ),
        "placeholder": (
            "எ.கா., உங்கள் கணக்கு முடக்கப்பட்டுள்ளது. KYC ஐப் புதுப்பிக்க"
            " http://... ஐக் கிளிக் செய்யவும்."
        ),
        "btn": "அச்சுறுத்தலைப் பகுப்பாய்வு செய் 🚀",
        "spinner": "செய்தி ஸ்கேன் செய்யப்படுகிறது...",
        "score_label": "அச்சுறுத்தல் மதிப்பெண்:",
        "high_risk": (
            "🛑 அதிக ஆபத்து: சாத்தியமான மோசடி அல்லது ஃபிஷிங் முயற்சி! கிளிக்"
            " செய்ய வேண்டாம்."
        ),
        "mod_risk": "⚠️ மிதமான ஆபத்து: எச்சரிக்கையுடன் தொடரவும்.",
        "low_risk": "✅ குறைந்த ஆபத்து: செய்தி பாதுகாப்பாகத் தெரிகிறது.",
        "reasons_title": "கண்டறிதல் காரணங்கள்:",
        "action_title": "பரிந்துரைக்கப்பட்ட நடவடிக்கை திட்டம்:",
        "no_input": "பகுப்பாய்வு செய்ய மேலே உரை அல்லது URL ஐ ஒட்டவும்.",
        "actions_high": [
            (
                "🚨 **எந்த இணைப்புகளையும் கிளிக் செய்ய வேண்டாம்** அல்லது"
                " ரகசியத் தகவல்களை (கடவுச்சொற்கள், OTP-கள், UPI PIN-கள்)"
                " உள்ளிட வேண்டாம்."
            ),
            (
                "📞 **உடனடியாகப் புகாரளிக்கவும்:** தேசிய சைபர் கிரைம் உதவி"
                " மையத்தை (**1930**) அழைக்கவும் அல்லது"
                " [cybercrime.gov.in](https://cybercrime.gov.in) இல்"
                " புகாரளிக்கவும்."
            ),
            (
                "🔒 **கணதுகளைப் பாதுகாக்க:** நீங்கள் விவரங்களை உள்ளிட்டிருந்தால்,"
                " உடனடியாக கடவுச்சொல்லை மாற்றி வங்கியைத் தொடர்பு கொள்ளவும்."
            ),
        ],
        "actions_mod": [
            (
                "⚠️ **தொடர்வதற்கு முன் சரிபார்க்கவும்:** SMS/இணைப்பில் உள்ள"
                " எண்களுக்குப் பதிலாக அதிகாரப்பூர்வ வலைத்தள எண்களைப்"
                " பயன்படுத்தவும்."
            ),
            (
                "🔍 **டொமைனைச் சரிபார்க்கவும்:** அனுப்புநரின் மின்னஞ்சல்"
                " முகவரி அல்லது வலைத்தள டொமைனை கவனமாகப் பரிசீலிக்கவும்."
            ),
            (
                "🛑 **அவசர கோரிக்கைகளைத் தவிர்க்கவும்:** செய்தி உங்களை"
                " உடனடியாகச் செயல்பட அழுத்தம் கொடுத்தால் கவனமாக இருக்கவும்."
            ),
        ],
        "actions_low": [
            "✅ **வழக்கமான எச்சரிக்கை:** வலுவான ஃபிஷிங் குறிகாட்டிகள் எதுவும்"
            " கண்டறியப்படவில்லை.",
            (
                "🔒 உள்நுழைவதற்கு முன் வலைத்தள URL `https://` இல் தொடங்குகிறது"
                " என்பதை உறுதிப்படுத்திக் கொள்ளவும்."
            ),
        ],
    },
}


# Enhanced Multi-Engine QR Code Extraction (PyZbar + OpenCV Fallbacks)
def extract_from_image(uploaded_file):
  try:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    # Method 1: PyZbar (Most powerful and reliable for all QR/Payment types)
    if PYZBAR_AVAILABLE:
      decoded_objects = pyzbar.decode(image)
      if decoded_objects:
        # Extract data from the first detected QR code
        qr_data = decoded_objects[0].data.decode("utf-8")
        if qr_data:
          return qr_data, True

    # Method 2: OpenCV QR Code Detector (Fallbacks)
    bgr_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()

    # Attempt A: Standard BGR
    data, _, _ = detector.detectAndDecode(bgr_img)
    if data:
      return data, True

    # Attempt B: Grayscale
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    data, _, _ = detector.detectAndDecode(gray)
    if data:
      return data, True

    # Attempt C: Thresholded Binary Image
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    data, _, _ = detector.detectAndDecode(thresh)
    if data:
      return data, True

    return None, False
  except Exception as e:
    return None, False


# Localization helper function for detection reasons
def get_localized_reason(reason, lang):
  translations = {
      "हिन्दी (Hindi)": {
          "Critical threat: Link contains a raw IP address instead of a domain.": (
              "गंभीर खतरा: लिंक में डोमेन के बजाय सीधे IP एड्रेस का उपयोग किया"
              " गया है।"
          ),
          "URL shortener detected (commonly used to hide malicious links).": (
              "URL शॉर्टनर का पता चला (आमतौर पर खतरनाक लिंक छिपाने के लिए"
              " उपयोग किया जाता है)।"
          ),
          "Suspicious domain extension detected.": (
              "संदिग्ध डोमेन एक्सटेंशन का पता चला।"
          ),
          "AI Text Model verified text as normal/safe.": (
              "AI टेक्स्ट मॉडल ने टेक्स्ट को सामान्य/सुरक्षित सत्यापित किया।"
          ),
      },
      "বাংলা (Bengali)": {
          "Critical threat: Link contains a raw IP address instead of a domain.": (
              "গুরুতর হুমকি: লিঙ্কে ডোমেনের পরিবর্তে সরাসরি IP ঠিকানা রয়েছে।"
          ),
          "URL shortener detected (commonly used to hide malicious links).": (
              "ইউআরএল শর্টনার সনাক্ত করা হয়েছে (সাধারণত ক্ষতিকারক লিঙ্ক লুকাতে"
              " ব্যবহৃত হয়)।"
          ),
          "Suspicious domain extension detected.": (
              "সন্দেহজনক ডোমেন এক্সটেনশন সনাক্ত করা হয়েছে।"
          ),
          "AI Text Model verified text as normal/safe.": (
              "AI টেক্সট মডেল পাঠ্যটিকে স্বাভাবিক/নিরাপদ বলে যাচাই করেছে।"
          ),
      },
      "मराठी (Marathi)": {
          "Critical threat: Link contains a raw IP address instead of a domain.": (
              "गंभीर धोका: दुव्यामध्ये डोमेनऐवजी थेट IP पत्ता आहे."
          ),
          "URL shortener detected (commonly used to hide malicious links).": (
              "URL शॉर्टर आढळले (सामान्यत: घातक दुवे लपवण्यासाठी वापरले"
              " जाते)."
          ),
          "Suspicious domain extension detected.": (
              "संशयास्पद डोमेन विस्तार आढळला."
          ),
          "AI Text Model verified text as normal/safe.": (
              "AI टेक्स्ट मॉडेलने मजकूर सामान्य/सुरक्षित म्हणून सत्यापित केला."
          ),
      },
      "తెలుగు (Telugu)": {
          "Critical threat: Link contains a raw IP address instead of a domain.": (
              "తీవ్రమైన ప్రమాదం: లింక్‌లో డొమైన్‌కి బదులుగా నేరుగా IP"
              " చిరునామా ఉంది."
          ),
          "URL shortener detected (commonly used to hide malicious links).": (
              "URL షార్ట్‌నర్ కనుగొనబడింది (సాధారణంగా హానికరమైన లింక్‌లను"
              " దాచడానికి ఉపయోగిస్తారు)."
          ),
          "Suspicious domain extension detected.": (
              "అనుమానాస్పద డొమైన్ పొడిగింపు కనుగొనబడింది."
          ),
          "AI Text Model verified text as normal/safe.": (
              "AI టెక్స్ట్ మోడల్ టెక్స్ట్‌ని సాధారణమైనదిగా/సురక్షితమైనదిగా"
              " ధృవీకరించింది."
          ),
      },
      "தமிழ் (Tamil)": {
          "Critical threat: Link contains a raw IP address instead of a domain.": (
              "கடுமையான அச்சுறுத்தல்: இணைப்பில் டொமைனுக்குப் பதிலாக நேரடி"
              " IP முகவரி உள்ளது."
          ),
          "URL shortener detected (commonly used to hide malicious links).": (
              "URL சுருக்கி கண்டறியப்பட்டது (பொதுவாக தீங்கிழைக்கும்"
              " இணைப்புகளை மறைக்கப் பயன்படுகிறது)."
          ),
          "Suspicious domain extension detected.": (
              "சந்தேகத்திற்கிடமான டொமைன் நீட்டிப்பு கண்டறியப்பட்டது."
          ),
          "AI Text Model verified text as normal/safe.": (
              "AI உரை மாதிரி உரையை சாதாரணமானது/பாதுகாப்பானது என"
              " சரிபார்த்தது."
          ),
      },
  }

  if lang in translations and reason in translations[lang]:
    return translations[lang][reason]

  if "High-risk scam/urgency keywords found:" in reason:
    keywords_part = reason.split(":")[-1]
    prefixes = {
        "हिन्दी (Hindi)": "उच्च जोखिम वाले घोटाले/तत्काल कीवर्ड मिले:",
        "বাংলা (Bengali)": "উচ্চ ঝুঁকিপূর্ণ স্ক্যাম/জরুরী কীওয়ার্ড পাওয়া গেছে:",
        "मराठी (Marathi)": "उच्च जोखमीचे घोटाळा/तातडीचे कीवर्ड आढळले:",
        "తెలుగు (Telugu)": (
            "అధిక ప్రమాదం గల స్కామ్/అత్యవసర కీవర్డ్‌లు కనుగొనబడ్డాయి:"
        ),
        "தமிழ் (Tamil)": (
            "அதிக ஆபத்துள்ள மோசடி/அவசர முக்கிய வார்த்தைகள் கண்டறியப்பட்டன:"
        ),
    }
    if lang in prefixes:
      return f"{prefixes[lang]} {keywords_part}"

  if "AI Text Model flagged phishing patterns" in reason:
    ai_prefixes = {
        "हिन्दी (Hindi)": "AI टेक्स्ट मॉडल ने फ़िशिंग पैटर्न का पता लगाया है",
        "বাংলা (Bengali)": "AI টেক্সট মডেল ফিশিং প্যাটার্ন চিহ্নিত করেছে",
        "मराठी (Marathi)": "AI टेक्स्ट मॉडेलने फिशिंग पॅटर्न ओळखले आहेत",
        "తెలుగు (Telugu)": "AI టెక్స్ట్ మోడల్ ఫిషింగ్ నమూనాలను గుర్తించింది",
        "தமிழ் (Tamil)": (
            "AI உரை மாதிரி ஃபிஷிங் வடிவங்களைக் கண்டறிந்துள்ளது"
        ),
    }
    if lang in ai_prefixes:
      suffix = reason[reason.find("(") :] if "(" in reason else ""
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

# Quishing Protection: QR Code / Screenshot Uploader
st.subheader(t["qr_section"])
uploaded_file = st.file_uploader(
    t["qr_upload"], type=["png", "jpg", "jpeg"]
)

qr_extracted_text = ""
if uploaded_file is not None:
  extracted_data, success = extract_from_image(uploaded_file)
  if success and extracted_data:
    st.success(f"{t['qr_success']} `{extracted_data}`")
    qr_extracted_text = extracted_data
  else:
    st.warning(t["qr_fail"])

st.markdown("---")

# Text Area input pre-filled if QR code URL is extracted
default_text = qr_extracted_text if qr_extracted_text else ""
user_input = st.text_area(
    t["input_label"], value=default_text, height=120, placeholder=t["placeholder"]
)

if st.button(t["btn"], use_container_width=True):
  if user_input.strip():
    with st.spinner(t["spinner"]):
      score, reasons = engine.analyze_input(user_input)

    st.markdown("---")
    st.subheader(f"{t['score_label']} {score} / 100")

    if score >= 60:
      st.error(t["high_risk"])
      action_items = t["actions_high"]
    elif score >= 25:
      st.warning(t["mod_risk"])
      action_items = t["actions_mod"]
    else:
      st.success(t["low_risk"])
      action_items = t["actions_low"]

    # Render Detection Reasons
    st.write(f"### {t['reasons_title']}")
    for reason in reasons:
      localized_reason = get_localized_reason(reason, selected_lang_name)
      st.write(f"- {localized_reason}")

    # Render Recommended Action Plan List
    st.write(f"### {t['action_title']}")
    for action in action_items:
      st.write(f"- {action}")
  else:
    st.info(t["no_input"])
