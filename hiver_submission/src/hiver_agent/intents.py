
INTENTS = ['ios_update_problem', 'battery_problem', 'device_performance_crash', 'app_problem', 'keyboard_input_problem', 'connectivity_problem', 'messaging_facetime_problem', 'apple_id_account_problem', 'hardware_device_problem', 'apple_watch_problem', 'icloud_media_storage_problem', 'purchase_order_billing', 'other_unknown']

KEYWORDS = {
"ios_update_problem": ["ios update","update ios","software update","cannot update","can't update","update failed","install update","download update","verify update"],
"battery_problem": ["battery","charging","charge","battery health","drain","dies","power"],
"device_performance_crash": ["crash","crashing","freeze","freezes","frozen","hang","hanging","restart","reboot","slow","lag","unresponsive","not responding"],
"app_problem": ["app","application","safari","camera","twitter","youtube","instagram"],
"keyboard_input_problem": ["keyboard","autocorrect","typing","type","keypress","key","character"],
"connectivity_problem": ["wifi","wi-fi","bluetooth","cellular","mobile data","internet","network","signal"],
"messaging_facetime_problem": ["imessage","i-message","messages","sms","facetime","face time"],
"apple_id_account_problem": ["apple id","appleid","password","two factor","2fa","verification code","sign in","login","account"],
"hardware_device_problem": ["screen","touchscreen","display","button","speaker","microphone","camera lens","keyboard key","broken","damaged","physical"],
"apple_watch_problem": ["apple watch","applewatch","watchos","watch"],
"icloud_media_storage_problem": ["icloud","icloud drive","icloud photos","photos sync","photo sync","storage"],
"purchase_order_billing": ["refund","purchase","purchased","order","payment","billing","charged","charge","subscription","gift card","trade-in","discount"]
}

def heuristic_intent(text):
    t=str(text).lower()
    # Specific/high-signal categories first.
    if any(k in t for k in KEYWORDS["apple_watch_problem"]): return "apple_watch_problem"
    if any(k in t for k in KEYWORDS["purchase_order_billing"]): return "purchase_order_billing"
    if any(k in t for k in KEYWORDS["apple_id_account_problem"]): return "apple_id_account_problem"
    if any(k in t for k in KEYWORDS["messaging_facetime_problem"]): return "messaging_facetime_problem"
    if any(k in t for k in KEYWORDS["keyboard_input_problem"]): return "keyboard_input_problem"
    if any(k in t for k in KEYWORDS["icloud_media_storage_problem"]): return "icloud_media_storage_problem"
    if any(k in t for k in KEYWORDS["connectivity_problem"]): return "connectivity_problem"
    if any(k in t for k in KEYWORDS["battery_problem"]): return "battery_problem"
    if any(k in t for k in KEYWORDS["ios_update_problem"]): return "ios_update_problem"
    if any(k in t for k in KEYWORDS["app_problem"]) and not any(k in t for k in ["app store","apps update"]): return "app_problem"
    if any(k in t for k in KEYWORDS["device_performance_crash"]): return "device_performance_crash"
    if any(k in t for k in KEYWORDS["hardware_device_problem"]): return "hardware_device_problem"
    return "other_unknown"
