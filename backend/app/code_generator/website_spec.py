"""Domain-driven website blueprints for the generated frontend.

Root cause of the "same website every time" bug
-----------------------------------------------
Previously the frontend generator always built the identical page structure
(Login, Dashboard, SectionOne, SectionTwo, Quick Access) and only swapped a few
text labels. This module centralizes *structural* site blueprints that depend on
the requested website type, so different prompts produce genuinely different
generated frontends: different pages, components, navigation, labels, data
models and UI.

It also centralises the multilingual dictionaries (English, Hindi, Kannada,
Marathi, Telugu) used by both the generated websites and the main dashboard UI.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Multi-language support
# ---------------------------------------------------------------------------

#: Language codes supported by generated sites and the main dashboard.
LANG_CODES: tuple[str, ...] = ("en", "hi", "kn", "mr", "te")

#: Native names shown in the language switcher (same spelling in every locale).
LANG_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "हिन्दी",
    "kn": "ಕನ್ನಡ",
    "mr": "मराठी",
    "te": "తెలుగు",
}

#: App-shell UI strings translated into every supported language.
#: ``{placeholder}`` tokens are substituted at runtime by the generated UI.
UI_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "appLabel": "App Dashboard",
        "dashboard": "Dashboard",
        "quickAccess": "Quick Access",
        "createNew": "Create New",
        "insights": "Reports & Insights",
        "signOut": "Sign Out",
        "notSignedIn": "Not signed in",
        "signInFirst": "Please sign in first to create a new record.",
        "signedOut": "You have been signed out.",
        "welcomeBack": "Welcome back, {email}! You are now signed in.",
        'createdSuccess': 'Created "{name}" successfully.',
        "createRecord": "Create New Record",
        "nameLabel": "Name",
        "namePlaceholder": "e.g. Enter a title",
        "cancel": "Cancel",
        "create": "Create",
        "language": "Language",
        "recentlyCreated": "Recently created",
        "noRecords": "No records yet. Click Create New to add one.",
        "signedInMsg": "✅ You are signed in as {user}.",
        "insightsSubtitle": "Items created in this workspace.",
        "insightsCol1": "Name",
        "insightsCol2": "Type",
        "insightsCol3": "Status",
        "insightsColCreated": "Created",
        "searchPlaceholder": "Search…",
        "siteLanguageHint": "Choose display language",
        "sections": "Sections",
        "overview": "Overview",
    },
    "hi": {
        "appLabel": "ऐप डैशबोर्ड",
        "dashboard": "डैशबोर्ड",
        "quickAccess": "त्वरित पहुँच",
        "createNew": "नया बनाएँ",
        "insights": "रिपोर्ट और अंतर्दृष्टि",
        "signOut": "साइन आउट",
        "notSignedIn": "साइन इन नहीं है",
        "signInFirst": "नया रिकॉर्ड बनाने के लिए पहले साइन इन करें।",
        "signedOut": "आप साइन आउट हो गए हैं।",
        "welcomeBack": "वापसी पर स्वागत है, {email}! आप साइन इन हैं।",
        'createdSuccess': '"{name}" सफलतापूर्वक बनाया गया।',
        "createRecord": "नया रिकॉर्ड बनाएँ",
        "nameLabel": "नाम",
        "namePlaceholder": "जैसे कोई शीर्षक दर्ज करें",
        "cancel": "रद्द करें",
        "create": "बनाएँ",
        "language": "भाषा",
        "recentlyCreated": "हाल में बनाए गए",
        "noRecords": "अभी कोई रिकॉर्ड नहीं। नया बनाने के लिए 'नया बनाएँ' पर क्लिक करें।",
        "signedInMsg": "✅ आप {user} के रूप में साइन इन हैं।",
        "insightsSubtitle": "इस कार्यक्षेत्र में बनाए गए आइटम।",
        "insightsCol1": "नाम",
        "insightsCol2": "प्रकार",
        "insightsCol3": "स्थिति",
        "insightsColCreated": "बनाया गया",
        "searchPlaceholder": "खोजें…",
        "siteLanguageHint": "प्रदर्शन भाषा चुनें",
        "sections": "अनुभाग",
        "overview": "अवलोकन",
    },
    "kn": {
        "appLabel": "ಆ್ಯಪ್ ಡ್ಯಾಶ್ಬೋರ್ಡ್",
        "dashboard": "ಡ್ಯಾಶ್ಬೋರ್ಡ್",
        "quickAccess": "ತ್ವರಿತ ಪ್ರವೇಶ",
        "createNew": "ಹೊಸದನ್ನು ರಚಿಸಿ",
        "insights": "ವರದಿಗಳು ಮತ್ತು ಒಳನೋಟಗಳು",
        "signOut": "ಸೈನ್ ಔಟ್",
        "notSignedIn": "ಸೈನ್ ಇನ್ ಆಗಿಲ್ಲ",
        "signInFirst": "ಹೊಸ ದಾಖಲೆ ರಚಿಸಲು ಮೊದಲು ಸೈನ್ ಇನ್ ಮಾಡಿ.",
        "signedOut": "ನೀವು ಸೈನ್ ಔಟ್ ಆಗಿದ್ದೀರಿ.",
        "welcomeBack": "ಮರಳಿ ಸ್ವಾಗತ, {email}! ನೀವು ಸೈನ್ ಇನ್ ಆಗಿದ್ದೀರಿ.",
        'createdSuccess': '"{name}" ಅನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ.',
        "createRecord": "ಹೊಸ ದಾಖಲೆ ರಚಿಸಿ",
        "nameLabel": "ಹೆಸರು",
        "namePlaceholder": "ಉದಾ: ಶೀರ್ಷಿಕೆಯನ್ನು ನಮೂದಿಸಿ",
        "cancel": "ರದ್ದುಮಾಡಿ",
        "create": "ರಚಿಸಿ",
        "language": "ಭಾಷೆ",
        "recentlyCreated": "ಇತ್ತೀಚೆಗೆ ರಚಿಸಲಾಗಿದೆ",
        "noRecords": "ಇನ್ನೂ ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲ. ಹೊಸದನ್ನು ರಚಿಸಲು 'ಹೊಸದನ್ನು ರಚಿಸಿ' ಕ್ಲಿಕ್ ಮಾಡಿ.",
        "signedInMsg": "✅ ನೀವು {user} ಆಗಿ ಸೈನ್ ಇನ್ ಆಗಿದ್ದೀರಿ.",
        "insightsSubtitle": "ಈ ಕಾರ್ಯಕ್ಷೇತ್ರದಲ್ಲಿ ರಚಿಸಲಾದ ಐಟಂಗಳು.",
        "insightsCol1": "ಹೆಸರು",
        "insightsCol2": "ಪ್ರಕಾರ",
        "insightsCol3": "ಸ್ಥಿತಿ",
        "insightsColCreated": "ರಚಿಸಲಾಗಿದೆ",
        "searchPlaceholder": "ಹುಡುಕಿ…",
        "siteLanguageHint": "ಪ್ರದರ್ಶನ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ",
        "sections": "ವಿಭಾಗಗಳು",
        "overview": "ಅವಲೋಕನ",
    },
    "mr": {
        "appLabel": "अ‍ॅप डॅशबोर्ड",
        "dashboard": "डॅशबोर्ड",
        "quickAccess": "जलद प्रवेश",
        "createNew": "नवीन तयार करा",
        "insights": "अहवाल आणि अंतर्दृष्टी",
        "signOut": "साइन आउट",
        "notSignedIn": "साइन इन केलेले नाही",
        "signInFirst": "नवीन रेकॉर्ड तयार करण्यासाठी प्रथम साइन इन करा.",
        "signedOut": "तुम्ही साइन आउट झाला आहात.",
        "welcomeBack": "पुन्हा स्वागत आहे, {email}! तुम्ही साइन इन आहात.",
        'createdSuccess': '"{name}" यशस्वीरित्या तयार केले.',
        "createRecord": "नवीन रेकॉर्ड तयार करा",
        "nameLabel": "नाव",
        "namePlaceholder": "उदा. शीर्षक प्रविष्ट करा",
        "cancel": "रद्द करा",
        "create": "तयार करा",
        "language": "भाषा",
        "recentlyCreated": "अलीकडे तयार केले",
        "noRecords": "अद्याप कोणतेही रेकॉर्ड नाहीत. नवीन तयार करण्यासाठी 'नवीन तयार करा' क्लिक करा.",
        "signedInMsg": "✅ तुम्ही {user} म्हणून साइन इन आहात.",
        "insightsSubtitle": "या कार्यक्षेत्रात तयार केलेल्या वस्तू.",
        "insightsCol1": "नाव",
        "insightsCol2": "प्रकार",
        "insightsCol3": "स्थिती",
        "insightsColCreated": "तयार केले",
        "searchPlaceholder": "शोधा…",
        "siteLanguageHint": "प्रदर्शन भाषा निवडा",
        "sections": "विभाग",
        "overview": "विहंगावलोकन",
    },
    "te": {
        "appLabel": "యాప్ డాష్బోర్డ్",
        "dashboard": "డాష్బోర్డ్",
        "quickAccess": "శీఘ్ర ప్రాప్యత",
        "createNew": "కొత్తది సృష్టించండి",
        "insights": "నివేదికలు మరియు అంతర్దృష్టులు",
        "signOut": "సైన్ అవుట్",
        "notSignedIn": "సైన్ ఇన్ చేయలేదు",
        "signInFirst": "కొత్త రికార్డ్ సృష్టించడానికి ముందుగా సైన్ ఇన్ చేయండి.",
        "signedOut": "మీరు సైన్ అవుట్ అయ్యారు.",
        "welcomeBack": "తిరిగి స్వాగతం, {email}! మీరు సైన్ ఇన్ అయ్యారు.",
        'createdSuccess': '"{name}" విజయవంతంగా సృష్టించబడింది.',
        "createRecord": "కొత్త రికార్డ్ సృష్టించండి",
        "nameLabel": "పేరు",
        "namePlaceholder": "ఉదా: శీర్షికను నమోదు చేయండి",
        "cancel": "రద్దు చేయండి",
        "create": "సృష్టించండి",
        "language": "భాష",
        "recentlyCreated": "ఇటీవల సృష్టించినవి",
        "noRecords": "ఇంకా రికార్డ్\u200cలు లేవు. కొత్తది సృష్టించడానికి 'కొత్తది సృష్టించండి' క్లిక్ చేయండి.",
        "signedInMsg": "✅ మీరు {user} గా సైన్ ఇన్ అయ్యారు.",
        "insightsSubtitle": "ఈ కార్యస్థలంలో సృష్టించిన అంశాలు.",
        "insightsCol1": "పేరు",
        "insightsCol2": "రకం",
        "insightsCol3": "స్థితి",
        "insightsColCreated": "సృష్టించబడింది",
        "searchPlaceholder": "వెతకండి…",
        "siteLanguageHint": "ప్రదర్శన భాషను ఎంచుకోండి",
        "sections": "విభాగాలు",
        "overview": "అవలోకనం",
    },
}
#: Domain vocabulary translated into every supported language. Keys are the
#: English terms used in generated navigation, metrics, sections and forms.
TERM_TRANSLATIONS: dict[str, dict[str, str]] = {
    "Patients": {"en": "Patients", "hi": "मरीज़", "kn": "ರೋಗಿಗಳು", "mr": "रुग्ण", "te": "రోగులు"},
    "Doctors": {"en": "Doctors", "hi": "डॉक्टर", "kn": "ವೈದ್ಯರು", "mr": "डॉक्टर", "te": "వైద్యులు"},
    "Appointments": {"en": "Appointments", "hi": "अपॉइंटमेंट", "kn": "ಅಪಾಯಿಂಟ್ಮೆಂಟ್‌ಗಳು", "mr": "भेटी", "te": "అపాయింట్‌మెంట్‌లు"},
    "Billing": {"en": "Billing", "hi": "बिलिंग", "kn": "ಬಿಲ್ಲಿಂಗ್", "mr": "बिलिंग", "te": "బిల్లింగ్"},
    "Pharmacy": {"en": "Pharmacy", "hi": "फार्मेसी", "kn": "ಔಷಧಾಲಯ", "mr": "औषधालय", "te": "ఫార్మసీ"},
    "Staff": {"en": "Staff", "hi": "स्टाफ", "kn": "ಸಿಬ್ಬಂದಿ", "mr": "कर्मचारी", "te": "సిబ్బంది"},
    "Products": {"en": "Products", "hi": "उत्पाद", "kn": "ಉತ್ಪನ್ನಗಳು", "mr": "उत्पादने", "te": "ఉత్పత్తులు"},
    "Orders": {"en": "Orders", "hi": "ऑर्डर", "kn": "ಆರ್ಡರ್‌ಗಳು", "mr": "ऑर्डर", "te": "ఆర్డర్‌లు"},
    "Customers": {"en": "Customers", "hi": "ग्राहक", "kn": "ಗ್ರಾಹಕರು", "mr": "ग्राहक", "te": "కస్టమర్‌లు"},
    "Cart": {"en": "Cart", "hi": "कार्ट", "kn": "ಕಾರ್ಟ್", "mr": "कार्ट", "te": "కార్ట్"},
    "Categories": {"en": "Categories", "hi": "श्रेणियाँ", "kn": "ವರ್ಗಗಳು", "mr": "श्रेण्या", "te": "వర్గాలు"},
    "Reviews": {"en": "Reviews", "hi": "समीक्षाएँ", "kn": "ವಿಮರ್ಶೆಗಳು", "mr": "पुनरावलोकने", "te": "సమీక్షలు"},
    "Restaurants": {"en": "Restaurants", "hi": "रेस्तरां", "kn": "ರೆಸ್ಟೋರೆಂಟ್‌ಗಳು", "mr": "रेस्टॉरंट", "te": "రెస్టారెంట్‌లు"},
    "Menu": {"en": "Menu", "hi": "मेनू", "kn": "ಮೆನು", "mr": "मेनू", "te": "మెనూ"},
    "Riders": {"en": "Riders", "hi": "डिलीवरी", "kn": "ರೈಡರ್‌ಗಳು", "mr": "डिलिव्हरी", "te": "రైడర్లు"},
    "Payments": {"en": "Payments", "hi": "भुगतान", "kn": "ಪಾವತಿಗಳು", "mr": "पेमेंट", "te": "చెల్లింపులు"},
    "Students": {"en": "Students", "hi": "छात्र", "kn": "ವಿದ್ಯಾರ್ಥಿಗಳು", "mr": "विद्यार्थी", "te": "విద్యార్థులు"},
    "Courses": {"en": "Courses", "hi": "पाठ्यक्रम", "kn": "ಕೋರ್ಸ್‌ಗಳು", "mr": "अभ्यासक्रम", "te": "కోర్సులు"},
    "Faculty": {"en": "Faculty", "hi": "शिक्षक", "kn": "ಬೋಧಕರು", "mr": "शिक्षक", "te": "అధ్యాపకులు"},
    "Attendance": {"en": "Attendance", "hi": "उपस्थिति", "kn": "ಹಾಜರಾತಿ", "mr": "उपस्थिती", "te": "హాజరు"},
    "Departments": {"en": "Departments", "hi": "विभाग", "kn": "ವಿಭಾಗಗಳು", "mr": "विभाग", "te": "విభాగాలు"},
    "Library": {"en": "Library", "hi": "पुस्तकालय", "kn": "ಗ್ರಂಥಾಲಯ", "mr": "वाचनालय", "te": "లైబ్రరీ"},
    "Accounts": {"en": "Accounts", "hi": "खाते", "kn": "ಖಾತೆಗಳು", "mr": "खाती", "te": "ఖాతాలు"},
    "Transactions": {"en": "Transactions", "hi": "लेनदेन", "kn": "ವಹಿವಾಟುಗಳು", "mr": "व्यवहार", "te": "లావాదేవీలు"},
    "Loans": {"en": "Loans", "hi": "ऋण", "kn": "ಸಾಲಗಳು", "mr": "कर्ज", "te": "రుణాలు"},
    "Reports": {"en": "Reports", "hi": "रिपोर्ट", "kn": "ವರದಿಗಳು", "mr": "अहवाल", "te": "నివేదికలు"},
    "Schedules": {"en": "Schedules", "hi": "समय-सारणी", "kn": "ವೇಳಾಪಟ್ಟಿಗಳು", "mr": "वेळापत्रक", "te": "షెడ్యూల్‌లు"},
    "Trains": {"en": "Trains", "hi": "ट्रेन", "kn": "ರೈಲುಗಳು", "mr": "गाड्या", "te": "రైళ్లు"},
    "Routes": {"en": "Routes", "hi": "मार्ग", "kn": "ಮಾರ್ಗಗಳು", "mr": "मार्ग", "te": "మార్గాలు"},
    "Stations": {"en": "Stations", "hi": "स्टेशन", "kn": "ನಿಲ್ದಾಣಗಳು", "mr": "स्थानके", "te": "స్టేషన్లు"},
    "Stock": {"en": "Stock", "hi": "स्टॉक", "kn": "ಸ್ಟಾಕ್", "mr": "ಸ್ಟಾಕ్", "te": "స్టాక్"},
    "Suppliers": {"en": "Suppliers", "hi": "आपूर्तिकर्ता", "kn": "ಪೂರೈಕೆದಾರರು", "mr": "ಪುರವಠಾದಾರ", "te": "సరఫరాదారులు"},
    "Shipments": {"en": "Shipments", "hi": "शिपमेंट", "kn": "ಸಾಗಣೆಗಳು", "mr": "पाठवणी", "te": "షిప్మెంట్లు"},
    "Warehouses": {"en": "Warehouses", "hi": "गोदाम", "kn": "ಗೋದಾಮುಗಳು", "mr": "गोदामे", "te": "గిడ్డంగులు"},
    "Properties": {"en": "Properties", "hi": "संपत्तियाँ", "kn": "ಆಸ್ತಿಗಳು", "mr": "मालमत्ता", "te": "ఆస్తులు"},
    "Listings": {"en": "Listings", "hi": "लिस्टिंग", "kn": "ಪಟ್ಟಿಗಳು", "mr": "याद्या", "te": "జాబితాలు"},
    "Agents": {"en": "Agents", "hi": "एजेंट", "kn": "ಏಜೆಂಟ್‌ಗಳು", "mr": "एजंट", "te": "ఏజెంట్లు"},
    "Clients": {"en": "Clients", "hi": "ग्राहक", "kn": "ಕ್ಲೈಂಟ್‌ಗಳು", "mr": "क्लायंट", "te": "క్లయింట్లు"},
    "Rooms": {"en": "Rooms", "hi": "कमरे", "kn": "ಕೊಠಡಿಗಳು", "mr": "खोल्या", "te": "గదులు"},
    "Bookings": {"en": "Bookings", "hi": "बुकिंग", "kn": "ಬುಕಿಂಗ್‌ಗಳು", "mr": "बुकिंग", "te": "బుకింగ్‌లు"},
    "Guests": {"en": "Guests", "hi": "मेहमान", "kn": "ಅತಿಥಿಗಳು", "mr": "पाहुणे", "te": "అతిథులు"},
    "Packages": {"en": "Packages", "hi": "पैकेज", "kn": "ಪ್ಯಾಕೇಜುಗಳು", "mr": "पॅकेजेस", "te": "ప్యాకేజీలు"},
    "Destinations": {"en": "Destinations", "hi": "गंतव्य", "kn": "ಸ್ಥಳಗಳು", "mr": "ठिकाणे", "te": "గమ్యస్థానాలు"},
    "Members": {"en": "Members", "hi": "सदस्य", "kn": "ಸದಸ್ಯರು", "mr": "सदस्य", "te": "సభ్యులు"},
    "Classes": {"en": "Classes", "hi": "कक्षाएँ", "kn": "ತರಗತಿಗಳು", "mr": "वर्ग", "te": "తరగతులు"},
    "Trainers": {"en": "Trainers", "hi": "प्रशिक्षक", "kn": "ತರಬೇತುದಾರರು", "mr": "प्रशिक्षक", "te": "శిక్షకులు"},
    "Plans": {"en": "Plans", "hi": "योजनाएँ", "kn": "ಯೋಜನೆಗಳು", "mr": "योजना", "te": "ప్రణాళికలు"},
    "Items": {"en": "Items", "hi": "आइटम", "kn": "ಐಟಂಗಳು", "mr": "आयटम", "te": "అంశాలు"},
    # ---- metrics ----
    "Total Patients": {"en": "Total Patients", "hi": "कुल मरीज़", "kn": "ಒಟ್ಟು ರೋಗಿಗಳು", "mr": "एकूण रुग्ण", "te": "మొత్తం రోగులు"},
    "Active Doctors": {"en": "Active Doctors", "hi": "सक्रिय डॉक्टर", "kn": "ಸಕ್ರಿಯ ವೈದ್ಯರು", "mr": "सक्रिय डॉक्टर", "te": "యాక్టివ్ వైద్యులు"},
    "Open Appointments": {"en": "Open Appointments", "hi": "खुले अपॉइंटमेंट", "kn": "ತೆರೆದ ಅಪಾಯಿಂಟ್ಮೆಂಟ್‌ಗಳು", "mr": "खुल्या भेटी", "te": "ఓపెన్ అపాయింట్మెంట్లు"},
    "Available Beds": {"en": "Available Beds", "hi": "उपलब्ध बिस्तर", "kn": "ಲಭ್ಯವಿರುವ ಹಾಸಿಗೆಗಳು", "mr": "उपलब्ध बेड", "te": "అందుబాటులో ఉన్న మంచాలు"},
    "Revenue": {"en": "Revenue", "hi": "राजस्व", "kn": "ಆದಾಯ", "mr": "महसूल", "te": "రెవెన్యూ"},
    "Active Carts": {"en": "Active Carts", "hi": "सक्रिय कार्ट", "kn": "సక్రియ కార్ట్\u200cలు", "mr": "सक्रिय कार्ट", "te": "యాక్టివ్ కార్ట్లు"},
    "Conversion": {"en": "Conversion", "hi": "रूपांतरण", "kn": "ಪರಿವರ್ತನೆ", "mr": "रूपांतरण", "te": "మార్పిడి రేటు"},
    "Enrolled Students": {"en": "Enrolled Students", "hi": "नामांकित छात्र", "kn": "ದಾಖಲಾದ ವಿದ್ಯಾರ್ಥಿಗಳು", "mr": "नोंदणीकृत विद्यार्थी", "te": "చేరిన విద్యార్థులు"},
    "Active Courses": {"en": "Active Courses", "hi": "सक्रिय पाठ्यक्रम", "kn": "సక్రియ కోర్సులు", "mr": "सक्रिय अभ्यासक्रम", "te": "యాక్టివ్ కోర్సులు"},
    "Attendance Today": {"en": "Attendance Today", "hi": "आज की उपस्थिति", "kn": "ಇಂದಿನ ಹಾಜರಾತಿ", "mr": "आजची उपस्थिती", "te": "నేటి హాజరు"},
    "Completion Rate": {"en": "Completion Rate", "hi": "पूर्णता दर", "kn": "ಪೂರ್ಣಗೊಳಿಸುವಿಕೆ ದರ", "mr": "पूर्णता दर", "te": "పూర్తి రేటు"},
    "Daily Orders": {"en": "Daily Orders", "hi": "दैनिक ऑर्डर", "kn": "ದೈನಂದಿನ ಆರ್ಡರ್\u200cಗಳು", "mr": "दैनिक ऑर्डर", "te": "రోజువారీ ఆర్డర్లు"},
    "Reservations": {"en": "Reservations", "hi": "आरक्षण", "kn": "ಮೀಸಲಾತಿಗಳು", "mr": "आरक्षण", "te": "రిజర్వేషన్లు"},
    "Available Tables": {"en": "Available Tables", "hi": "उपलब्ध टेबल", "kn": "ಲಭ್ಯವಿರುವ ಟೇಬಲ್\u200cಗಳು", "mr": "उपलब्ध टेबल", "te": "అందుబాటులో ఉన్న టేబుళ్లు"},
    "Customer Rating": {"en": "Customer Rating", "hi": "ग्राहक रेटिंग", "kn": "ಗ್ರಾಹಕ ರೇಟಿಂಗ್", "mr": "ग्राहक रेटिंग", "te": "కస్టమర్ రేటింగ్"},
    "Total Balance": {"en": "Total Balance", "hi": "कुल शेष", "kn": "ಒಟ್ಟು ಬಾಕಿ", "mr": "एकूण शिल्लक", "te": "మొత్తం బ్యాలెన్స్"},
    "New Customers": {"en": "New Customers", "hi": "नए ग्राहक", "kn": "ಹೊಸ ಗ್ರಾಹಕರು", "mr": "नवीन ग्राहक", "te": "కొత్త కస్టమర్లు"},
    "Approval Rate": {"en": "Approval Rate", "hi": "स्वीकृति दर", "kn": "ಅನುಮೋದನೆ ದರ", "mr": "मंजुरी दर", "te": "ఆమోదం రేటు"},
    "In-stock Items": {"en": "In-stock Items", "hi": "स्टॉक में आइटम", "kn": "ಸ್ಟಾಕ್\u200cನಲ್ಲಿರುವ ವಸ್ತುಗಳು", "mr": "स्टॉकमधील वस्तू", "te": "స్టాక్లో అంశాలు"},
    "Low Stock": {"en": "Low Stock", "hi": "कम स्टॉक", "kn": "ಕಡಿಮೆ ಸ್ಟಾಕ್", "mr": "कमी स्टॉक", "te": "తక్కువ స్టాక్"},
    "Turnover": {"en": "Turnover", "hi": "टर्नओवर", "kn": "ಟರ್ನೋವರ್", "mr": "टर्नओव्हर", "te": "టర్నోవర్"},
    "Active Restaurants": {"en": "Active Restaurants", "hi": "सक्रिय रेस्तरां", "kn": "ಸಕ್ರಿಯ ರೆಸ್ಟೋರೆಂಟ್\u200cಗಳು", "mr": "सक्रिय रेस्टॉरंट", "te": "యాక్టివ్ రెస్టారెంట్లు"},
    "Active Riders": {"en": "Active Riders", "hi": "सक्रिय राइडर", "kn": "ಸక్రಿಯ ರೈಡರ್\u200cಗಳು", "mr": "सक्रिय राइडर्स", "te": "యాక్టివ్ రైడర్లు"},
    "Avg Delivery Time": {"en": "Avg Delivery Time", "hi": "औसत डिलीवरी समय", "kn": "ಸರಾಸರಿ ವಿತರಣಾ ಸಮಯ", "mr": "सरासरी डिलिव्हरी वेळ", "te": "సగటు డెలివరీ సమయం"},
    "Listed Properties": {"en": "Listed Properties", "hi": "सूचीबद्ध संपत्तियाँ", "kn": "ಪಟ್ಟಿ ಮಾಡಿದ ಆಸ್ತಿಗಳು", "mr": "सूचीबद्ध मालमत्ता", "te": "జాబితా ఆస్తులు"},
    "Active Listings": {"en": "Active Listings", "hi": "सक्रिय लिस्टिंग", "kn": "సక్రియ పట్టికలు", "mr": "सक्रिय याद्या", "te": "యాక్టివ్ జాబితాలు"},
    "Available Rooms": {"en": "Available Rooms", "hi": "उपलब्ध कमरे", "kn": "ಲಭ್ಯವಿರುವ ಕೊಠಡಿಗಳು", "mr": "उपलब्ध खोल्या", "te": "అందుబాటులో ఉన్న గదులు"},
    "Occupancy": {"en": "Occupancy", "hi": "अधिभोग", "kn": "ಆಕ್ಯುಪೆನ್ಸಿ", "mr": "अधिभोग", "te": "ఆక్యుపెన్సీ"},
    "Check-ins": {"en": "Check-ins", "hi": "चेक-इन", "kn": "ಚೆಕ್-ಇನ್\u200cಗಳು", "mr": "चेक-इन", "te": "చెక్-ఇన్లు"},
    "Bookings Today": {"en": "Bookings Today", "hi": "आज की बुकिंग", "kn": "ಇಂದಿನ ಬುಕಿಂಗ್\u200cಗಳು", "mr": "आजची बुकिंग", "te": "నేటి బుకింగ్లు"},
    "Travelers": {"en": "Travelers", "hi": "यात्री", "kn": "ಪ್ರಯಾಣಿಕರು", "mr": "प्रवासी", "te": "ప్రయాణికులు"},
    "Active Packages": {"en": "Active Packages", "hi": "सक्रिय पैकेज", "kn": "ಸಕ್ರಿಯ ಪ್ಯಾಕೇಜುಗಳು", "mr": "सक्रिय पॅकेजेस", "te": "యాక్టివ్ ప్యాకేజీలు"},
    "Total Members": {"en": "Total Members", "hi": "कुल सदस्य", "kn": "ಒಟ್ಟು ಸದಸ್ಯರು", "mr": "एकूण सदस्य", "te": "మొత్తం సభ్యులు"},
    "Classes Today": {"en": "Classes Today", "hi": "आज की कक्षाएँ", "kn": "ಇಂದಿನ ತರಗತಿಗಳು", "mr": "आजचे वर्ग", "te": "నేటి తరగతులు"},
    "Active Trainers": {"en": "Active Trainers", "hi": "सक्रिय प्रशिक्षक", "kn": "సక్రియ తరబేతుదారులు", "mr": "सक्रिय प्रशिक्षक", "te": "యాక్టివ్ శిక్షకులు"},
    "Plan Renewals": {"en": "Plan Renewals", "hi": "योजना नवीनीकरण", "kn": "ಯೋಜನಾ ನವೀಕರಣಗಳು", "mr": "योजना नूतनीकरण", "te": "ప్లాన్ పునరుద్ధరణలు"},
    "Total Items": {"en": "Total Items", "hi": "कुल आइटम", "kn": "ಒಟ್ಟು ಐಟಂಗಳು", "mr": "एकूण आयटम", "te": "మొత్తం అంశాలు"},
    "Active Now": {"en": "Active Now", "hi": "अभी सक्रिय", "kn": "ಈಗ ಸಕ್ರಿಯ", "mr": "सध्या सक्रिय", "te": "ఇప్పుడు యాక్టివ్"},
    "Good Rating": {"en": "Good Rating", "hi": "अच्छी रेटिंग", "kn": "ಉತ್ತಮ ರೇಟಿಂಗ్", "mr": "चांगली रेटिंग", "te": "మంచి రేటింగ్"},
}
# ---------------------------------------------------------------------------
# Domain → website blueprint
# ---------------------------------------------------------------------------

def _translated(term: str) -> dict[str, str]:
    """Return the 5-language dictionary for a domain term (fallback to term)."""
    return TERM_TRANSLATIONS.get(term, {"en": term, "hi": term, "kn": term, "mr": term, "te": term})


#: Each spec controls the *structure* of the generated site: navigation items,
#: named components generated + rendered, metric cards, the record data model
#: used by the "create record" modal and insights table, plus generic copy.
_SPEC_COMMON: dict[str, Any] = {
    "app_label": "App Dashboard",
    "nav": [{"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"}],
    "components": [],
    "metrics": [],
    "record": {
        "name_label": _translated("Name"),
        "name_placeholder": "e.g. Enter a title",
        "field2_label": _translated("Items"),
        "field3_label": _translated("Reports"),
        "field2_placeholder": "e.g. Add a detail",
        "field3_placeholder": "e.g. Select status",
        "field2_default": "General",
        "field3_default": "Active",
        "table_headers": ["Name", "Type", "Status", "Created"],
    },
    "insights_title": _translated("Reports"),
    "insights_empty": "No records yet. Click Create New to add one.",
}

_SPECS: dict[str, dict[str, Any]] = {
    "hospital": {
        "app_label": "Health Dashboard",
        "keywords": ("hospital", "medical", "clinic", "patient", "doctor", "healthcare", "appointment", "nurse", "medicine"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "patients", "id": "section-1", "label": _translated("Patients"), "component": "Patients"},
            {"key": "doctors", "id": "section-2", "label": _translated("Doctors"), "component": "Doctors"},
            {"key": "appointments", "id": "section-3", "label": _translated("Appointments"), "component": "Appointments"},
            {"key": "billing", "id": "section-4", "label": _translated("Billing"), "component": "Billing"},
        ],
        "components": ["Patients", "Doctors", "Appointments", "Billing"],
        "metrics": [
            {"label": _translated("Total Patients"), "value": "1,280"},
            {"label": _translated("Active Doctors"), "value": "72"},
            {"label": _translated("Open Appointments"), "value": "34"},
            {"label": _translated("Available Beds"), "value": "18"},
        ],
        "record": {
            "name_label": _translated("Patient"),
            "name_placeholder": "e.g. Ravi Kumar",
            "field2_label": _translated("Departments"),
            "field3_label": _translated("Staff"),
            "field2_placeholder": "e.g. Cardiology",
            "field3_placeholder": "e.g. Admitted",
            "field2_default": "General Ward",
            "field3_default": "Admitted",
            "table_headers": ["Patient", "Department", "Status", "Admitted"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No patient records yet. Click Create New to add one.",
    },
    "ecommerce": {
        "app_label": "Commerce Dashboard",
        "keywords": ("e-commerce", "ecommerce", "shop", "store", "product", "cart", "order", "checkout", "retail"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "products", "id": "section-1", "label": _translated("Products"), "component": "Products"},
            {"key": "orders", "id": "section-2", "label": _translated("Orders"), "component": "Orders"},
            {"key": "customers", "id": "section-3", "label": _translated("Customers"), "component": "Customers"},
            {"key": "categories", "id": "section-4", "label": _translated("Categories"), "component": "Categories"},
        ],
        "components": ["Products", "Orders", "Customers", "Categories"],
        "metrics": [
            {"label": _translated("Revenue"), "value": "$86.2K"},
            {"label": _translated("Orders"), "value": "453"},
            {"label": _translated("Active Carts"), "value": "127"},
            {"label": _translated("Conversion"), "value": "4.6%"},
        ],
        "record": {
            "name_label": _translated("Products"),
            "name_placeholder": "e.g. Wireless Headphones",
            "field2_label": _translated("Categories"),
            "field3_label": _translated("Stock"),
            "field2_placeholder": "e.g. Electronics",
            "field3_placeholder": "e.g. In Stock",
            "field2_default": "General",
            "field3_default": "In Stock",
            "table_headers": ["Product", "Category", "Price", "Stock"],
        },
        "insights_title": _translated("Orders"),
        "insights_empty": "No orders yet. Click Create New to add a product.",
    },
    "food_delivery": {
        "app_label": "Food Delivery Dashboard",
        "keywords": ("food", "delivery", "restaurant", "menu", "chef", "dining", "swiggy", "zomato", "foodie"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "restaurants", "id": "section-1", "label": _translated("Restaurants"), "component": "Restaurants"},
            {"key": "menu", "id": "section-2", "label": _translated("Menu"), "component": "Menu"},
            {"key": "orders", "id": "section-3", "label": _translated("Orders"), "component": "Orders"},
            {"key": "riders", "id": "section-4", "label": _translated("Riders"), "component": "Riders"},
        ],
        "components": ["Restaurants", "Menu", "Orders", "Riders"],
        "metrics": [
            {"label": _translated("Daily Orders"), "value": "128"},
            {"label": _translated("Active Restaurants"), "value": "45"},
            {"label": _translated("Active Riders"), "value": "62"},
            {"label": _translated("Avg Delivery Time"), "value": "28 min"},
        ],
        "record": {
            "name_label": _translated("Menu"),
            "name_placeholder": "e.g. Paneer Biryani",
            "field2_label": _translated("Restaurants"),
            "field3_label": _translated("Orders"),
            "field2_placeholder": "e.g. Spice Garden",
            "field3_placeholder": "e.g. Delivered",
            "field2_default": "Home Kitchen",
            "field3_default": "Preparing",
            "table_headers": ["Dish", "Restaurant", "Price", "Status"],
        },
        "insights_title": _translated("Orders"),
        "insights_empty": "No food orders yet. Click Create New to add a dish.",
    },
    "education": {
        "app_label": "Campus Dashboard",
        "keywords": ("college", "collage", "university", "school", "student", "course", "teacher", "faculty", "attendance", "exam", "campus"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "students", "id": "section-1", "label": _translated("Students"), "component": "Students"},
            {"key": "courses", "id": "section-2", "label": _translated("Courses"), "component": "Courses"},
            {"key": "faculty", "id": "section-3", "label": _translated("Faculty"), "component": "Faculty"},
            {"key": "attendance", "id": "section-4", "label": _translated("Attendance"), "component": "Attendance"},
        ],
        "components": ["Students", "Courses", "Faculty", "Attendance"],
        "metrics": [
            {"label": _translated("Enrolled Students"), "value": "3,420"},
            {"label": _translated("Active Courses"), "value": "92"},
            {"label": _translated("Faculty"), "value": "48"},
            {"label": _translated("Attendance Today"), "value": "96%"},
        ],
        "record": {
            "name_label": _translated("Students"),
            "name_placeholder": "e.g. Ananya Sharma",
            "field2_label": _translated("Courses"),
            "field3_label": _translated("Attendance"),
            "field2_placeholder": "e.g. B.Sc Computer Science",
            "field3_placeholder": "e.g. Active",
            "field2_default": "General",
            "field3_default": "Active",
            "table_headers": ["Student", "Course", "Year", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No student records yet. Click Create New to add one.",
    },
    "finance": {
        "app_label": "Finance Dashboard",
        "keywords": ("bank", "finance", "banking", "account", "transaction", "loan", "balance", "credit", "ledger"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "accounts", "id": "section-1", "label": _translated("Accounts"), "component": "Accounts"},
            {"key": "transactions", "id": "section-2", "label": _translated("Transactions"), "component": "Transactions"},
            {"key": "loans", "id": "section-3", "label": _translated("Loans"), "component": "Loans"},
            {"key": "customers", "id": "section-4", "label": _translated("Customers"), "component": "Customers"},
        ],
        "components": ["Accounts", "Transactions", "Loans", "Customers"],
        "metrics": [
            {"label": _translated("Total Balance"), "value": "$1.8M"},
            {"label": _translated("Transactions"), "value": "2,140"},
            {"label": _translated("New Customers"), "value": "312"},
            {"label": _translated("Approval Rate"), "value": "91%"},
        ],
        "record": {
            "name_label": _translated("Accounts"),
            "name_placeholder": "e.g. Savings Account",
            "field2_label": _translated("Transactions"),
            "field3_label": _translated("Loans"),
            "field2_placeholder": "e.g. Credit",
            "field3_placeholder": "e.g. Active",
            "field2_default": "Current",
            "field3_default": "Active",
            "table_headers": ["Account", "Type", "Balance", "Status"],
        },
        "insights_title": _translated("Transactions"),
        "insights_empty": "No transactions yet. Click Create New to add an account.",
    },
    "inventory": {
        "app_label": "Inventory Dashboard",
        "keywords": ("inventory", "stock", "warehouse", "supplier", "shipment", "sku", "logistics"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "stock", "id": "section-1", "label": _translated("Stock"), "component": "Stock"},
            {"key": "suppliers", "id": "section-2", "label": _translated("Suppliers"), "component": "Suppliers"},
            {"key": "shipments", "id": "section-3", "label": _translated("Shipments"), "component": "Shipments"},
            {"key": "warehouses", "id": "section-4", "label": _translated("Warehouses"), "component": "Warehouses"},
        ],
        "components": ["Stock", "Suppliers", "Shipments", "Warehouses"],
        "metrics": [
            {"label": _translated("In-stock Items"), "value": "4,100"},
            {"label": _translated("Low Stock"), "value": "73"},
            {"label": _translated("Shipments"), "value": "18"},
            {"label": _translated("Turnover"), "value": "2.4x"},
        ],
        "record": {
            "name_label": _translated("Items"),
            "name_placeholder": "e.g. LED Bulb (Box)",
            "field2_label": _translated("Categories"),
            "field3_label": _translated("Stock"),
            "field2_placeholder": "e.g. Electricals",
            "field3_placeholder": "e.g. In Stock",
            "field2_default": "General",
            "field3_default": "In Stock",
            "table_headers": ["Item", "Category", "Stock", "Supplier"],
        },
        "insights_title": _translated("Stock"),
        "insights_empty": "No inventory items yet. Click Create New to add one.",
    },
    "real_estate": {
        "app_label": "Real Estate Dashboard",
        "keywords": ("real estate", "property", "listing", "agent", "broker", "apartment", "villa", "buyer"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "properties", "id": "section-1", "label": _translated("Properties"), "component": "Properties"},
            {"key": "listings", "id": "section-2", "label": _translated("Listings"), "component": "Listings"},
            {"key": "agents", "id": "section-3", "label": _translated("Agents"), "component": "Agents"},
            {"key": "clients", "id": "section-4", "label": _translated("Clients"), "component": "Clients"},
        ],
        "components": ["Properties", "Listings", "Agents", "Clients"],
        "metrics": [
            {"label": _translated("Listed Properties"), "value": "312"},
            {"label": _translated("Active Listings"), "value": "148"},
            {"label": _translated("Agents"), "value": "24"},
            {"label": _translated("Customers"), "value": "560"},
        ],
        "record": {
            "name_label": _translated("Properties"),
            "name_placeholder": "e.g. Skyline Apartment 3BHK",
            "field2_label": _translated("Agents"),
            "field3_label": _translated("Listings"),
            "field2_placeholder": "e.g. Priya Realty",
            "field3_placeholder": "e.g. For Sale",
            "field2_default": "Direct",
            "field3_default": "For Sale",
            "table_headers": ["Property", "Agent", "Price", "Status"],
        },
        "insights_title": _translated("Listings"),
        "insights_empty": "No listings yet. Click Create New to add a property.",
    },
    "hospitality": {
        "app_label": "Hotel Dashboard",
        "keywords": ("hotel", "hospitality", "resort", "room", "guest", "check-in", "hotal"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "rooms", "id": "section-1", "label": _translated("Rooms"), "component": "Rooms"},
            {"key": "bookings", "id": "section-2", "label": _translated("Bookings"), "component": "Bookings"},
            {"key": "guests", "id": "section-3", "label": _translated("Guests"), "component": "Guests"},
            {"key": "staff", "id": "section-4", "label": _translated("Staff"), "component": "Staff"},
        ],
        "components": ["Rooms", "Bookings", "Guests", "Staff"],
        "metrics": [
            {"label": _translated("Available Rooms"), "value": "42"},
            {"label": _translated("Bookings Today"), "value": "18"},
            {"label": _translated("Check-ins"), "value": "11"},
            {"label": _translated("Occupancy"), "value": "78%"},
        ],
        "record": {
            "name_label": _translated("Rooms"),
            "name_placeholder": "e.g. Deluxe King Room",
            "field2_label": _translated("Guests"),
            "field3_label": _translated("Bookings"),
            "field2_placeholder": "e.g. Aman Verma",
            "field3_placeholder": "e.g. Reserved",
            "field2_default": "Walk-in",
            "field3_default": "Available",
            "table_headers": ["Room", "Guest", "Check-in", "Status"],
        },
        "insights_title": _translated("Bookings"),
        "insights_empty": "No bookings yet. Click Create New to add a room.",
    },
    "travel": {
        "app_label": "Travel Dashboard",
        "keywords": ("travel", "tour", "tourism", "flight", "airline", "destination", "trip", "holiday"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "packages", "id": "section-1", "label": _translated("Packages"), "component": "Packages"},
            {"key": "bookings", "id": "section-2", "label": _translated("Bookings"), "component": "Bookings"},
            {"key": "destinations", "id": "section-3", "label": _translated("Destinations"), "component": "Destinations"},
            {"key": "guests", "id": "section-4", "label": _translated("Guests"), "component": "Guests"},
        ],
        "components": ["Packages", "Bookings", "Destinations", "Guests"],
        "metrics": [
            {"label": _translated("Active Packages"), "value": "86"},
            {"label": _translated("Bookings Today"), "value": "33"},
            {"label": _translated("Travelers"), "value": "1,204"},
            {"label": _translated("Customer Rating"), "value": "4.7★"},
        ],
        "record": {
            "name_label": _translated("Packages"),
            "name_placeholder": "e.g. Goa Beach Tour",
            "field2_label": _translated("Destinations"),
            "field3_label": _translated("Bookings"),
            "field2_placeholder": "e.g. Goa, India",
            "field3_placeholder": "e.g. Confirmed",
            "field2_default": "Domestic",
            "field3_default": "Available",
            "table_headers": ["Package", "Destination", "Price", "Status"],
        },
        "insights_title": _translated("Bookings"),
        "insights_empty": "No travel bookings yet. Click Create New to add a package.",
    },
    "fitness": {
        "app_label": "Fitness Dashboard",
        "keywords": ("fitness", "gym", "workout", "yoga", "health club", "trainer", "sports"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "members", "id": "section-1", "label": _translated("Members"), "component": "Members"},
            {"key": "classes", "id": "section-2", "label": _translated("Classes"), "component": "Classes"},
            {"key": "trainers", "id": "section-3", "label": _translated("Trainers"), "component": "Trainers"},
            {"key": "plans", "id": "section-4", "label": _translated("Plans"), "component": "Plans"},
        ],
        "components": ["Members", "Classes", "Trainers", "Plans"],
        "metrics": [
            {"label": _translated("Total Members"), "value": "856"},
            {"label": _translated("Classes Today"), "value": "24"},
            {"label": _translated("Active Trainers"), "value": "18"},
            {"label": _translated("Plan Renewals"), "value": "112"},
        ],
        "record": {
            "name_label": _translated("Members"),
            "name_placeholder": "e.g. Kabir Singh",
            "field2_label": _translated("Plans"),
            "field3_label": _translated("Classes"),
            "field2_placeholder": "e.g. Monthly",
            "field3_placeholder": "e.g. Active",
            "field2_default": "Basic",
            "field3_default": "Active",
            "table_headers": ["Member", "Plan", "Joined", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No member records yet. Click Create New to add one.",
    },
    "railway": {
        "app_label": "Railway Operations",
        "keywords": ("railway", "railroad", "rail", "reilve", "train", "locomotive", "rail station", "railway station"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "trains", "id": "section-1", "label": _translated("Trains"), "component": "Trains"},
            {"key": "routes", "id": "section-2", "label": _translated("Routes"), "component": "Routes"},
            {"key": "stations", "id": "section-3", "label": _translated("Stations"), "component": "Stations"},
            {"key": "bookings", "id": "section-4", "label": _translated("Bookings"), "component": "Bookings"},
            {"key": "schedules", "id": "section-5", "label": _translated("Schedules"), "component": "Schedules"},
        ],
        "components": ["Trains", "Routes", "Stations", "Bookings", "Schedules"],
        "metrics": [
            {"label": _translated("Active Trains")},
            {"label": _translated("Scheduled Routes")},
            {"label": _translated("Stations")},
            {"label": _translated("Bookings Today")},
        ],
        "record": {
            "name_label": _translated("Trains"),
            "name_placeholder": "e.g. Express 204",
            "field2_label": _translated("Routes"),
            "field3_label": _translated("Status"),
            "field2_placeholder": "e.g. Central to North",
            "field3_placeholder": "e.g. On Time",
            "field2_default": "Central Line",
            "field3_default": "On Time",
            "table_headers": ["Train", "Route", "Departure", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No train records yet. Click Create New to add one.",
    },
    "transit": {
        "app_label": "Transit & Fleet Operations",
        "keywords": ("bus", "busses", "citybus", "city bus", "transit", "fleet", "metro", "transport", "transportation", "commute", "ticket", "shuttle", "depot"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "buses", "id": "section-1", "label": _translated("Buses"), "component": "Buses"},
            {"key": "routes", "id": "section-2", "label": _translated("Routes"), "component": "Routes"},
            {"key": "drivers", "id": "section-3", "label": _translated("Drivers"), "component": "Drivers"},
            {"key": "schedules", "id": "section-4", "label": _translated("Schedules"), "component": "Schedules"},
            {"key": "bookings", "id": "section-5", "label": _translated("Bookings"), "component": "Bookings"},
        ],
        "components": ["Buses", "Routes", "Drivers", "Schedules", "Bookings"],
        "metrics": [
            {"label": _translated("Active Buses")},
            {"label": _translated("Scheduled Routes")},
            {"label": _translated("Drivers on Duty")},
            {"label": _translated("Passenger Bookings")},
        ],
        "record": {
            "name_label": _translated("Buses"),
            "name_placeholder": "e.g. Bus 402 - Express Line",
            "field2_label": _translated("Routes"),
            "field3_label": _translated("Status"),
            "field2_placeholder": "e.g. Downtown to Terminal",
            "field3_placeholder": "e.g. On Time",
            "field2_default": "Route 101",
            "field3_default": "Active",
            "table_headers": ["Bus", "Route", "Driver", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No bus records yet. Click Create New to add one.",
    },
    "temple": {
        "app_label": "Temple Operations",
        "keywords": ("temple", "mandir", "pooja", "puja", "devotee", "darshan", "prasad", "deity", "ashram"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "devotees", "id": "section-1", "label": _translated("Devotees"), "component": "Devotees"},
            {"key": "poojabookings", "id": "section-2", "label": _translated("Pooja Bookings"), "component": "PoojaBookings"},
            {"key": "donations", "id": "section-3", "label": _translated("Donations"), "component": "Donations"},
            {"key": "events", "id": "section-4", "label": _translated("Events"), "component": "Events"},
            {"key": "priests", "id": "section-5", "label": _translated("Priests"), "component": "Priests"},
        ],
        "components": ["Devotees", "PoojaBookings", "Donations", "Events", "Priests"],
        "metrics": [
            {"label": _translated("Devotees Today")},
            {"label": _translated("Scheduled Poojas")},
            {"label": _translated("Donations Received")},
            {"label": _translated("Upcoming Events")},
        ],
        "record": {
            "name_label": _translated("Devotees"),
            "name_placeholder": "e.g. Ramesh Patel",
            "field2_label": _translated("Pooja Bookings"),
            "field3_label": _translated("Status"),
            "field2_placeholder": "e.g. Morning Aarti",
            "field3_placeholder": "e.g. Confirmed",
            "field2_default": "Special Darshan",
            "field3_default": "Confirmed",
            "table_headers": ["Devotee", "Service", "Date", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No devotee records yet. Click Create New to add one.",
    },
    "agriculture": {
        "app_label": "Agriculture Portal",
        "keywords": ("agri", "agriculture", "farmer", "farm", "crop", "crops", "harvest", "cultivation", "irrigation", "seed", "fertilizer", "soil"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "crops", "id": "section-1", "label": _translated("Crops"), "component": "Crops"},
            {"key": "farmers", "id": "section-2", "label": _translated("Farmers"), "component": "Farmers"},
            {"key": "equipment", "id": "section-3", "label": _translated("Equipment"), "component": "Equipment"},
            {"key": "harvests", "id": "section-4", "label": _translated("Harvests"), "component": "Harvests"},
            {"key": "inventory", "id": "section-5", "label": _translated("Inventory"), "component": "Inventory"},
        ],
        "components": ["Crops", "Farmers", "Equipment", "Harvests", "Inventory"],
        "metrics": [
            {"label": _translated("Active Crops")},
            {"label": _translated("Registered Farmers")},
            {"label": _translated("Farm Equipment")},
            {"label": _translated("Seasonal Yields")},
        ],
        "record": {
            "name_label": _translated("Crops"),
            "name_placeholder": "e.g. Wheat Crop Lot A",
            "field2_label": _translated("Farmers"),
            "field3_label": _translated("Status"),
            "field2_placeholder": "e.g. Northern Field",
            "field3_placeholder": "e.g. Growing",
            "field2_default": "Field 1",
            "field3_default": "Growing",
            "table_headers": ["Crop", "Farmer / Field", "Yield", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No crop records yet. Click Create New to add one.",
    },
    "task": {
        "app_label": "Task Dashboard",
        "keywords": ("task", "tasks", "todo", "project management", "issue tracker", "bug tracker", "kanban", "tasks"),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "tasks", "id": "section-1", "label": _translated("Tasks"), "component": "Tasks"},
            {"key": "projects", "id": "section-2", "label": _translated("Projects"), "component": "Projects"},
            {"key": "team", "id": "section-3", "label": _translated("Team"), "component": "Team"},
        ],
        "components": ["Tasks", "Projects", "Team"],
        "metrics": [
            {"label": _translated("Total Tasks"), "value": "1,240"},
            {"label": _translated("In Progress"), "value": "82%"},
            {"label": _translated("Completed"), "value": "5,300"},
            {"label": _translated("Team Members"), "value": "14%"},
        ],
        "record": {
            "name_label": _translated("Tasks"),
            "name_placeholder": "e.g. Fix login bug",
            "field2_label": _translated("Projects"),
            "field3_label": _translated("Team"),
            "field2_placeholder": "e.g. Website Redesign",
            "field3_placeholder": "e.g. Active",
            "field2_default": "General",
            "field3_default": "Active",
            "table_headers": ["Task", "Project", "Assignee", "Status"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No tasks yet. Click Create New to add one.",
    },
    "generic": {
        "app_label": "Generated Project",
        "keywords": (),
        "nav": [
            {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"},
            {"key": "overview", "id": "section-1", "label": _translated("Overview"), "component": "Overview"},
            {"key": "records", "id": "section-2", "label": _translated("Records"), "component": "Records"},
            {"key": "activities", "id": "section-3", "label": _translated("Activities"), "component": "Activities"},
            {"key": "analytics", "id": "section-4", "label": _translated("Analytics"), "component": "Analytics"},
        ],
        "components": ["Overview", "Records", "Activities", "Analytics"],
        "metrics": [
            {"label": _translated("Active Users"), "value": "1,240"},
            {"label": _translated("Task Completion"), "value": "82%"},
            {"label": _translated("Engagement"), "value": "5,300"},
            {"label": _translated("Growth"), "value": "14%"},
        ],
        "record": {
            "name_label": _translated("Name"),
            "name_placeholder": "e.g. Enter a title",
            "field2_label": _translated("Items"),
            "field3_label": _translated("Reports"),
            "field2_placeholder": "e.g. Add a detail",
            "field3_placeholder": "e.g. Select status",
            "field2_default": "General",
            "field3_default": "Active",
            "table_headers": ["Name", "Type", "Status", "Created"],
        },
        "insights_title": _translated("Reports"),
        "insights_empty": "No records yet. Click Create New to add one.",
    },
}
#: Final domain → merged spec (common structure + domain overrides).
WEBSITE_SPECS: dict[str, dict[str, Any]] = {}
for _key, _spec in _SPECS.items():
    merged: dict[str, Any] = {}
    merged.update(_SPEC_COMMON)
    merged.update(_spec)
    WEBSITE_SPECS[_key] = merged

#: Longest keyword lists are matched first so more-specific sites win.
_SPEC_ORDER: list[tuple[tuple[str, ...], str]] = []
for _key, _spec in WEBSITE_SPECS.items():
    _SPEC_ORDER.append((_spec["keywords"], _key))
_SPEC_ORDER.sort(key=lambda item: len(item[0]), reverse=True)

#: Project-type names surfaced in requirement analysis and the main UI.
PROJECT_TYPE_NAMES: dict[str, str] = {
    "generic": "General",
    "hospital": "Healthcare",
    "ecommerce": "E-Commerce",
    "food_delivery": "Food Delivery",
    "education": "Education",
    "finance": "Finance",
    "inventory": "Inventory",
    "real_estate": "Real Estate",
    "hospitality": "Hospitality",
    "railway": "Railway",
    "transit": "Transit & Fleet",
    "temple": "Temple Heritage",
    "agriculture": "Agriculture",
    "travel": "Travel",
    "fitness": "Fitness",
    "task": "Task Management",
}

#: Domain → module names surfaced in requirement analysis and the main UI.
#: Domain detection priority (higher = more specific / wins ties).
_SPEC_PRIORITY: dict[str, int] = {
    "education": 50,
    "food_delivery": 40,
    "hospital": 35,
    "hospitality": 45,
    "travel": 30,
    "real_estate": 30,
    "finance": 25,
    "inventory": 25,
    "fitness": 25,
    "transit": 34,
    "temple": 34,
    "agriculture": 34,
    "railway": 32,
    "ecommerce": 20,
    "task": 20,
    "generic": 0,
}


def detect_website_key(text: str) -> str:
    """Return the website blueprint key with the most keyword matches.

    Uses a scoring approach: for each spec, count how many of its keywords
    appear in the normalized prompt. The spec with the highest match count
    wins. Ties are broken by ``_SPEC_PRIORITY`` so more specific domains
    (e.g. ``food_delivery``) beat generic ones (``ecommerce``).
    """
    normalized = (text or "").casefold()
    best_key = "generic"
    best_score = 0
    best_priority = -1

    for keywords, key in _SPEC_ORDER:
        score = sum(
            1
            for kw in keywords
            if re.search(rf"(?<!\w){re.escape(kw.casefold())}(?!\w)", normalized)
        )
        if score == 0:
            continue
        priority = _SPEC_PRIORITY.get(key, 0)
        if score > best_score or (score == best_score and priority > best_priority):
            best_score = score
            best_key = key
            best_priority = priority
    return best_key
PROJECT_TYPE_MODULES: dict[str, list[str]] = {
    "hospital": ["Patients", "Doctors", "Appointments", "Billing", "Pharmacy", "Staff"],
    "ecommerce": ["Products", "Orders", "Customers", "Cart", "Categories", "Reviews"],
    "food_delivery": ["Restaurants", "Menu", "Orders", "Riders", "Payments", "Reviews"],
    "education": ["Students", "Courses", "Faculty", "Attendance", "Departments", "Library"],
    "finance": ["Accounts", "Transactions", "Loans", "Customers", "Cards", "Reports"],
    "inventory": ["Products", "Stock", "Suppliers", "Shipments", "Warehouses", "Categories"],
    "real_estate": ["Properties", "Listings", "Agents", "Clients", "Bookings", "Payments"],
    "hospitality": ["Rooms", "Bookings", "Guests", "Menu", "Staff", "Payments"],
    "travel": ["Packages", "Bookings", "Hotels", "Guests", "Destinations", "Payments"],
    "fitness": ["Members", "Classes", "Trainers", "Plans", "Attendance", "Payments"],
    "railway": ["Trains", "Routes", "Stations", "Bookings", "Schedules", "Staff"],
    "transit": ["Buses", "Routes", "Drivers", "Schedules", "Bookings", "Stops"],
    "temple": ["Devotees", "PoojaBookings", "Donations", "Events", "Priests", "Services"],
    "agriculture": ["Crops", "Farmers", "Equipment", "Harvests", "Inventory", "Suppliers"],
    "task": ["Tasks", "Projects", "Team", "Boards", "Comments", "Attachments"],
}


def derive_website_type_name(prompt: str) -> str:
    """Return a human-readable project type (e.g. 'Healthcare') for a prompt."""
    return PROJECT_TYPE_NAMES.get(detect_website_key(prompt), "General")


def derive_website_modules(prompt: str) -> list[str]:
    """Return module names detected for the prompt's website type."""
    key = detect_website_key(prompt)
    modules = list(PROJECT_TYPE_MODULES.get(key, []))
    # Include explicit module keywords mentioned in the prompt when available.
    explicit = ("Dashboard", "Login", "Admin")
    for module in explicit:
        if module.lower() in (prompt or "").lower() and module not in modules:
            modules.insert(0, module)
    return modules


def _derive_custom_modules(prompt: str) -> list[str]:
    """Extract explicitly listed user-defined resources for otherwise unknown domains."""
    stop_prefixes = ("a ", "an ", "the ", "all ", "our ", "your ")
    stop_items = {"and", "or", "with", "including", "etc", "more", "user", "users", "system", "application", "app", "platform"}
    found: list[str] = []
    for match in re.finditer(
        r"\b(?:manage|track|organize|monitor|record|include)\s+(?:(?:the|all|our|your)\s+)?([^.!?;\n]+)"
        r"|\b(?:modules?|sections?|pages?)\s*(?:for|include|are)?\s*:?\s*([^.!?;\n]+)",
        prompt or "",
        flags=re.IGNORECASE,
    ):
        phrase = match.group(1) or match.group(2) or ""
        phrase = re.split(r"\b(?:using|built|based|so that|which|that|with|for)\b", phrase, maxsplit=1, flags=re.IGNORECASE)[0]
        for item in re.split(r",|\band\b|\bor\b|&|\bplus\b", phrase, flags=re.IGNORECASE):
            cleaned = re.sub(r"\s+", " ", item.strip(" \t\r\n'\"`"))
            while any(cleaned.casefold().startswith(prefix) for prefix in stop_prefixes):
                cleaned = cleaned[len(cleaned.split(" ", 1)[0]) + 1:].strip()
            words = cleaned.split()
            if not cleaned or len(words) > 4 or cleaned.casefold() in stop_items:
                continue
            if cleaned.casefold() not in {name.casefold() for name in found}:
                found.append(cleaned.title())
            if len(found) == 10:
                return found
    return found


def derive_website_spec(prompt: str, project_name: str = "") -> dict[str, Any]:
    """Build a website blueprint, honoring an explicit domain in the app name."""
    normalized_project_name = re.sub(r"[_-]+", " ", project_name).strip()
    project_key = detect_website_key(normalized_project_name) if normalized_project_name else "generic"
    title_identifies_application = bool(
        re.search(r"\b(management|system|platform|operations)\b", normalized_project_name.casefold())
    )
    key = (
        project_key
        if project_key != "generic" and title_identifies_application
        else detect_website_key(prompt)
    )
    spec: dict[str, Any] = {}
    spec.update(WEBSITE_SPECS[key])
    components = list(spec.get("components", []))
    module_labels: dict[str, str] = dict(spec.get("module_labels", {}))
    navigation = list(spec.get("nav", []))

    def add_module(label: str) -> None:
        component = re.sub(r"[^A-Za-z0-9]", "", label.title()) or "Resource"
        if not component[0].isalpha():
            component = f"Resource{component}"
        if any(existing.casefold() == component.casefold() for existing in components):
            return
        components.append(component)
        module_labels[component] = label
        navigation.append({
            "key": term_key(label),
            "id": f"section-{len(components)}",
            "label": _translated(label),
            "component": component,
        })

    if key == "generic":
        custom_modules = _derive_custom_modules(prompt)
        if custom_modules:
            spec["components"] = []
            spec["module_labels"] = {}
            spec["nav"] = [
                {"key": "dashboard", "id": "dashboard", "label": _translated("Dashboard"), "component": "Dashboard"}
            ]
            components = spec["components"]
            module_labels = spec["module_labels"]
            navigation = spec["nav"]
            for module in custom_modules:
                add_module(module)
            spec["record"] = dict(spec["record"])
            spec["record"]["name_label"] = _translated(custom_modules[0])
            spec["record"]["table_headers"] = [custom_modules[0], "Category", "Status", "Created"]

    if key != "generic":
        normalized_prompt = (prompt or "").casefold()
        for module in PROJECT_TYPE_MODULES.get(key, []):
            singular = module[:-1] if module.casefold().endswith("s") else module
            if any(
                re.search(rf"(?<!\w){re.escape(candidate.casefold())}(?!\w)", normalized_prompt)
                for candidate in {module, singular}
            ):
                add_module(module)

        for module in _derive_custom_modules(prompt):
            if any(existing.casefold() == module.casefold() for existing in module_labels.values()):
                continue
            add_module(module)

    spec["components"] = components
    spec["module_labels"] = module_labels
    spec["nav"] = navigation
    spec["key"] = key
    spec["project_type"] = PROJECT_TYPE_NAMES.get(key, "General")
    spec["app_label"] = project_name.strip() or WEBSITE_SPECS[key]["app_label"]
    spec["metrics"] = [
        {"label": metric["label"]}
        for metric in spec.get("metrics", [])
        if "label" in metric
    ]
    return spec
# ---------------------------------------------------------------------------
# Multilingual dictionary generation helpers
# ---------------------------------------------------------------------------

def build_language_dictionaries(spec: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Expand a website spec into per-language flat dictionaries (keys → text).

    The result mirrors the `translations` object emitted into the generated
    ``src/languages.ts`` file and used by the main dashboard.
    """
    dictionaries: dict[str, dict[str, str]] = {code: dict(UI_TRANSLATIONS[code]) for code in LANG_CODES}

    used_terms: set[str] = set()
    for nav_item in spec.get("nav", ()):
        term = nav_item.get("label", {}).get("en", "")
        if term:
            used_terms.add(term)
    for metric in spec.get("metrics", ()):
        term = metric.get("label", {}).get("en", "")
        if term:
            used_terms.add(term)
    for field_key in ("name_label", "field2_label", "field3_label"):
        term = spec.get("record", {}).get(field_key, {}).get("en", "")
        if term:
            used_terms.add(term)

    for term in used_terms:
        translations = TERM_TRANSLATIONS.get(term)
        if not translations:
            continue
        for code in LANG_CODES:
            dictionaries[code][term_key(term)] = translations[code]

    dictionaries["en"]["appLabel"] = spec["app_label"]
    return dictionaries


def term_key(term: str) -> str:
    """Convert an English domain term into a stable camelCase translation key."""
    words = [word for word in term.replace("&", "And").replace("/", " ").split(" ") if word]
    return words[0].lower() + "".join(word[:1].upper() + word[1:] for word in words[1:])