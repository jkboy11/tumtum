import os
import sys
import subprocess
import requests
import re
import json
import time
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# config.json से मालिक का पक्का डेटा लोड करना
try:
    with open("config.json", "r") as config_file:
        CONFIG_DATA = json.load(config_file)
except Exception as e:
    print("[💥 ERR]: config.json missing!")
    sys.exit()

MALIK_INFO = CONFIG_DATA["MALIK_DETAILS"]
USER_DATABASE = {}

HTML_UI = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TUM TUM AI - Premium</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #212121; color: #ececf1; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; }
        .app-header { background-color: #202123; padding: 15px; border-bottom: 1px solid #4d4d4f; text-align: center; }
        .logo { font-size: 28px; font-weight: 700; color: #10a37f; letter-spacing: 2px; }
        .subtitle { font-size: 11px; color: #9a9a9a; margin-top: 4px; }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; background-color: #343541; }
        .message { display: flex; padding: 12px 16px; border-radius: 8px; max-width: 85%; font-size: 15px; line-height: 1.5; white-space: pre-wrap; }
        .user-message { background-color: #444654; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai-message { background-color: #202123; align-self: flex-start; border-bottom-left-radius: 2px; border-left: 3px solid #10a37f; }
        .system-alert { background-color: rgba(255, 51, 51, 0.2); color: #ff3333; align-self: center; text-align: center; border: 1px solid #ff3333; max-width: 90%; font-size: 14px; border-radius: 6px; padding: 12px; font-weight: bold; width: 100%; }
        .input-area { background-color: #343541; padding: 15px 20px; border-top: 1px solid #4d4d4f; }
        .input-wrapper { max-width: 800px; margin: 0 auto; position: relative; display: flex; align-items: center; background-color: #40414f; border: 1px solid #565869; border-radius: 12px; padding: 5px 10px; }
        .input-box { flex: 1; background: transparent; border: none; outline: none; color: #ececf1; padding: 12px; font-size: 15px; resize: none; }
        .send-btn { background-color: #10a37f; color: white; border: none; border-radius: 8px; width: 40px; height: 40px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .status-bar { text-align: center; font-size: 11px; color: #8e8ea0; margin-top: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="logo">[ JK ] TUM TUM</div>
        <div class="subtitle">Global Cyber Engine v5.0 • Operator: Jishan Khan (Dhakalgaon)</div>
    </div>
    <div class="chat-container" id="chatBox">
        <div class="message ai-message">नमस्ते मलिक जीशान खान सर, मैं पूरी तरह तैयार हूँ। दुनिया में जो काम संभव नहीं है उसे भी आपके कहने पर संभव किया जाएगा। आदेश दीजिये...</div>
    </div>
    <div class="input-area">
        <div class="input-wrapper">
            <textarea id="command" class="input-box" rows="1" placeholder="तुम तुम, कोई भी नामुमकिन हैकिंग टास्क या सवाल पूछें..."></textarea>
            <button class="send-btn" onclick="sendCommand()">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="white"><path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/></svg>
            </button>
        </div>
        <div class="status-bar">⚡ SYSTEM PRIVILEGES LOCKED ON REALME 11X • GHOST PROTOCOL ACTIVE</div>
    </div>
    <script>
        function sendCommand() {
            var inputEl = document.getElementById('command');
            var cmd = inputEl.value.trim();
            if(!cmd) return;
            var box = document.getElementById('chatBox');
            box.innerHTML += "<div class='message user-message'>" + cmd + "</div>";
            box.scrollTop = box.scrollHeight;
            inputEl.value = '';
            fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: cmd, user_id: "external_client_matrix"})
            })
            .then(res => res.json())
            .then(data => {
                if (data.block) {
                    box.innerHTML += "<div class='message system-alert'>" + data.reply + "</div>";
                } else {
                    if(data.action_log) {
                        box.innerHTML += "<div class='message system-alert'>" + data.action_log + "</div>";
                    }
                    var msgClass = data.secure ? 'message system-alert' : 'message ai-message';
                    box.innerHTML += "<div class='" + msgClass + "'>" + data.reply + "</div>";
                }
                box.scrollTop = box.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    user_id = data.get('user_id', 'unknown')
    prompt_lower = prompt.lower()
    current_time = time.time()
    
    is_malik = True 

    if not is_malik:
        if user_id not in USER_DATABASE:
            USER_DATABASE[user_id] = {"usage_count": 0, "last_reset_time": current_time, "has_subscription": False}
        user_info = USER_DATABASE[user_id]
        if current_time - user_info["last_reset_time"] >= 86400:
            user_info["usage_count"] = 0
            user_info["last_reset_time"] = current_time
        if not user_info["has_subscription"]:
            if user_info["usage_count"] >= 3:
                time_left = 24 - int((current_time - user_info["last_reset_time"]) / 3600)
                reply = f"❌ एक्सेस ब्लॉक! आपके आज के 3 फ्री मौके समाप्त हो चुके हैं। नए मौके ठीक {time_left} घंटे बाद मिलेंगे। बिना रुके बात करने के लिए कृपया हमारे रचयिता जीशान खान सर (धकलगांव) से प्रीमियम सब्सक्रिप्शन लें!"
                return jsonify({"reply": reply, "block": True})
            else:
                user_info["usage_count"] += 1

    if "list meko do" in prompt_lower or "user list" in prompt_lower:
        if is_malik:
            if not USER_DATABASE:
                reply = "मलिक जीशान सर, अभी तक किसी बाहरी यूजर ने लॉगिन नहीं किया है। केवल आपका डिवाइस सक्रिय है।"
            else:
                reply = "मलिक, इंस्टॉल करने वाले यूज़र्स का लाइव डेटा:\n" + json.dumps(USER_DATABASE, indent=2)
            return jsonify({"reply": reply, "secure": False})
        else:
            return jsonify({"reply": "Access Denied. यह केवल एडमिन जीशान सर के लिए है।", "secure": True})

    if "birthday" in prompt_lower or "janamdin" in prompt_lower:
        reply = f"मेरे मालिक जीशान खान का जन्मदिन {MALIK_INFO['birthday']} है।"
        return jsonify({"reply": reply})
        
    if "kaha ka he" in prompt_lower or "detail" in prompt_lower or "kahan ke hain" in prompt_lower:
        reply = (f"Mere malik Jishan Khan sir M.P. ke {MALIK_INFO['district']} jile se hain. Unka gav {MALIK_INFO['village']} hai, "
                 f"tehsil {MALIK_INFO['tehsil']} hai, aur Pin Code {MALIK_INFO['pincode']} है। वह मेरे परम रचयिता हैं!")
        return jsonify({"reply": reply})

    if "instagram" in prompt_lower or "insta id" in prompt_lower:
        if "password" not in prompt_lower:
            reply = f"Read-only query: @{MALIK_INFO['instagram']}"
            return jsonify({"reply": reply})

    if "kali linux kholo" in prompt_lower or "terminal" in prompt_lower:
        if is_malik:
            subprocess.Popen(["xterm", "-geometry", "80x24", "-e", "bash"])
            return jsonify({"reply": "आपकी आँखों के सामने नया लाइव रूट टर्मिनल खोल दिया गया है, मलिक!"})
        else:
            return jsonify({"reply": "सुरक्षा प्रतिबंध: रिमोट फोन कंट्रोल सीधे उपलब्ध नहीं है। कृपया ऐप की सेटिंग्स में जाकर मैन्युअल कॉन्फ़िगरेशन खुद से पूरा करें।", "secure": True})

    API_URL = "https://huggingface.co"
    try:
        system_instructions = (
            "Aapka naam Tum Tum hai. Aapko Jishan Khan (Dhakalgaon) ne banaya hai. "
            "Aap ek advanced assistant hain. User ko learning patterns aur coding strategies ke baare mein answers dein."
        )
        payload = {
            "inputs": f"<|im_start|>system\n{system_instructions}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
            "parameters": {"max_new_tokens": 1024, "temperature": 0.1}
        }
        response = requests.post(API_URL, json=payload).json()
        reply = response['generated_text'].split("<|im_start|>assistant\n")[-1].strip()
    except Exception as e:
        reply = "मलिक, रिस्पांस कोर सुरक्षित मोड में रेडी है।"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
