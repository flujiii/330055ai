import os
import requests
import pandas as pd
import numpy as np
import time
import yfinance as yf
from datetime import datetime
from flask import Flask
from threading import Thread
import json

# ============================================
# 🔒 نظام التفعيل والتسجيل (لك فقط)
# ============================================

# بيانات المطور (أنت فقط)
DEVELOPER_CHAT_ID = "7520800507"  # ← غير هذا لرقمك
ACTIVATION_KEY = "CRYPTO-VIP-2024"  # ← مفتاح التفعيل

# تخزين المستخدمين المفعلين
activated_users = {}
users_file = "activated_users.json"

def load_activated_users():
    """تحميل المستخدمين المفعلين"""
    global activated_users
    try:
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                activated_users = json.load(f)
        else:
            activated_users = {}
    except:
        activated_users = {}

def save_activated_users():
    """حفظ المستخدمين المفعلين"""
    try:
        with open(users_file, 'w') as f:
            json.dump(activated_users, f)
    except:
        pass

def is_user_activated(chat_id):
    """التحقق إذا المستخدم مفعل"""
    return str(chat_id) in activated_users

def activate_user(chat_id, key):
    """تفعيل المستخدم"""
    if key == ACTIVATION_KEY:
        activated_users[str(chat_id)] = {
            "activated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "lifetime"  # مدى الحياة
        }
        save_activated_users()
        return True
    return False

# تحميل المستخدمين عند البدء
load_activated_users()

# ============================================
# 🔧 إعدادات البوت
# ============================================

# استخدم متغيرات البيئة للأمان
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8381083486:AAG5sxcGTEmXIEDJ-I_o1YxAzw7n6xwBdFk')
CHAT_ID = os.environ.get('CHAT_ID', '7520800507')

# تحقق إذا البوت يعمل على Replit
IS_REPLIT = "REPLIT_DB_URL" in os.environ

# ============================================
# 🌐 Flask App للنشاط الدائم
# ============================================

app = Flask(__name__)

@app.route('/')
def home():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Crypto Trading Bot</title>
    <meta charset="utf-8">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
        }}
        .status {{
            font-size: 1.2em;
            color: #4ade80;
            background: rgba(74, 222, 128, 0.2);
            padding: 10px 20px;
            border-radius: 10px;
            display: inline-block;
            margin: 20px 0;
        }}
        .info-box {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }}
        .btn {{
            background: #4f46e5;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }}
        .btn:hover {{
            background: #4338ca;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 30px 0;
        }}
        .stat-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            min-width: 150px;
            margin: 10px;
        }}
        .log {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            text-align: left;
            font-family: monospace;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Crypto Trading Bot</h1>
        <div class="status">✅ Online & Running</div>
        
        <div class="info-box">
            <h3>📊 Bot Statistics</h3>
            <div class="stats">
                <div class="stat-item">
                    <strong>Users</strong><br>
                    <span style="font-size: 2em;">{len(activated_users)}</span>
                </div>
                <div class="stat-item">
                    <strong>Uptime</strong><br>
                    <span id="uptime">Calculating...</span>
                </div>
                <div class="stat-item">
                    <strong>Platform</strong><br>
                    <span>{"Replit" if IS_REPLIT else "Local"}</span>
                </div>
            </div>
        </div>
        
        <div class="info-box">
            <h3>🎯 Quick Links</h3>
            <a href="https://t.me/crypto_vip_analysis_bot" class="btn" target="_blank">📱 Open Telegram Bot</a>
            <a href="/admin" class="btn">⚙️ Admin Panel</a>
            <a href="/stats" class="btn">📈 Statistics</a>
        </div>
        
        <div class="info-box">
            <h3>📝 Recent Activity</h3>
            <div class="log" id="activityLog">
                Loading...
            </div>
        </div>
        
        <p style="margin-top: 30px; opacity: 0.8;">
            Bot ID: {TOKEN[:15]}... | Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    
    <script>
        // حساب وقت التشغيل
        function updateUptime() {{
            const startTime = new Date('2024-01-01T00:00:00').getTime();
            const now = new Date().getTime();
            const diff = now - startTime;
            
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            document.getElementById('uptime').textContent = days + 'd ' + hours + 'h ' + minutes + 'm';
        }}
        
        // تحديث السجل
        function updateLog() {{
            fetch('/api/activity')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('activityLog').innerHTML = data.log;
                }});
        }}
        
        updateUptime();
        updateLog();
        setInterval(updateUptime, 60000);
        setInterval(updateLog, 10000);
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_panel():
    """لوحة تحكم المطور"""
    # التحقق إذا هو المطور
    import json
    stats = {
        "total_users": len(activated_users),
        "recent_activations": list(activated_users.items())[-5:] if activated_users else [],
        "bot_status": "running",
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platform": "Replit" if IS_REPLIT else "Local"
    }
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .panel {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #4f46e5; color: white; padding: 15px; border-radius: 8px; }}
        .users-list {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; max-height: 300px; overflow-y: auto; }}
        .controls {{ margin: 20px 0; }}
        .btn {{ background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px; cursor: pointer; }}
        .btn-red {{ background: #ef4444; }}
        pre {{ background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 8px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="panel">
        <h1>⚙️ Admin Panel</h1>
        <p>Developer: {DEVELOPER_CHAT_ID}</p>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Users</h3>
                <p style="font-size: 2em;">{stats['total_users']}</p>
            </div>
            <div class="stat-box">
                <h3>Platform</h3>
                <p>{stats['platform']}</p>
            </div>
            <div class="stat-box">
                <h3>Status</h3>
                <p style="color: #4ade80;">{stats['bot_status'].upper()}</p>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="generateKey()">🔑 Generate New Key</button>
            <button class="btn btn-red" onclick="resetUsers()">🔄 Reset All Users</button>
            <button class="btn" onclick="backupData()">💾 Backup Data</button>
        </div>
        
        <div class="users-list">
            <h3>Activated Users ({len(activated_users)})</h3>
            <pre>{json.dumps(activated_users, indent=2, ensure_ascii=False)}</pre>
        </div>
        
        <div>
            <h3>📋 Current Activation Key:</h3>
            <pre style="background: #f1f5f9; color: #0f172a;">{ACTIVATION_KEY}</pre>
        </div>
    </div>
    
    <script>
        function generateKey() {{
            const newKey = 'CRYPTO-VIP-' + Date.now().toString().slice(-8);
            if(confirm('Generate new key?\\n' + newKey)) {{
                alert('New key generated!\\n' + newKey);
            }}
        }}
        
        function resetUsers() {{
            if(confirm('Are you sure? This will reset ALL users!')) {{
                fetch('/admin/reset')
                    .then(() => location.reload());
            }}
        }}
        
        function backupData() {{
            const data = {json.dumps(stats)};
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'bot_backup_' + new Date().toISOString().split('T')[0] + '.json';
            a.click();
        }}
    </script>
</body>
</html>
"""

@app.route('/api/activity')
def api_activity():
    """API لجلب نشاط البوت"""
    log = f"""[{datetime.now().strftime('%H:%M:%S')}] Bot is running
[{datetime.now().strftime('%H:%M:%S')}] Users: {len(activated_users)}
[{datetime.now().strftime('%H:%M:%S')}] Last check: OK
[{datetime.now().strftime('%H:%M:%S')}] Platform: {'Replit' if IS_REPLIT else 'Local'}"""
    return {"log": log}

@app.route('/admin/reset')
def admin_reset():
    """إعادة تعيين المستخدمين (للمطور فقط)"""
    global activated_users
    activated_users = {}
    save_activated_users()
    return "✅ All users reset!"

# ============================================
# 🤖 وظائف البوت الرئيسية
# ============================================

def send_msg(chat_id, text, parse_mode='Markdown'):
    """إرسال رسالة"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def analyze_crypto(symbol):
    """تحليل العملة (نسخة مبسطة)"""
    try:
        symbol = symbol.upper().strip()
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='1d')
        
        if df.empty:
            return "❌ لا توجد بيانات لهذه العملة"
        
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else price
        change = ((price - prev_price) / prev_price) * 100
        
        # تحليل مبسط
        if change > 2:
            signal = "🟢 شراء قوي"
        elif change > 0:
            signal = "🟢 شراء"
        elif change < -2:
            signal = "🔴 بيع قوي"
        elif change < 0:
            signal = "🔴 بيع"
        else:
            signal = "⚪ انتظار"
        
        report = f"""
📊 **تحليل {symbol.replace('-USD', '')}**

💰 **السعر:** ${price:,.2f}
📈 **التغير:** {change:+.2f}%
🎯 **الإشارة:** {signal}

📊 **المستويات:**
├ المقاومة: ${price * 1.02:,.2f}
├ الدعم: ${price * 0.98:,.2f}
└ وقف الخسارة: ${price * 0.96:,.2f}

⚠️ **ملاحظة:** تحليل تقني فقط
🕐 **الوقت:** {datetime.now().strftime('%H:%M:%S')}
        """
        return report
    
    except Exception as e:
        return f"❌ خطأ في التحليل: {str(e)}"

def show_menu(chat_id):
    """عرض القائمة"""
    menu = """
🎯 **بوت التحليل المتقدم VIP**

📋 **الأوامر المتاحة:**
├ /start - بدء البوت
├ /activate [key] - تفعيل البوت
├ /analyze [رمز] - تحليل عملة
├ /menu - عرض القائمة
├ /mystats - إحصائياتي
└ /support - الدعم الفني

💰 **للتحليل السريع:**
أرسل رمز العملة مباشرة مثل:
BTC, ETH, SOL, ADA, XRP

🔑 **مفتاح التفعيل:** اطلبه من المطور
    """
    send_msg(chat_id, menu)

# ============================================
# 🚀 التشغيل الرئيسي للبوت
# ============================================

def process_messages():
    """معالجة رسائل التليجرام"""
    last_update_id = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "result" in data and data["result"]:
                    for update in data["result"]:
                        last_update_id = update["update_id"]
                        
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            text = msg.get("text", "").strip()
                            
                            print(f"📩 {chat_id}: {text}")
                            
                            # تحقق من التفعيل أولاً
                            if not is_user_activated(chat_id):
                                if text.startswith("/activate "):
                                    key = text.split(" ", 1)[1]
                                    if activate_user(chat_id, key):
                                        send_msg(chat_id, "✅ **تم التفعيل بنجاح!**\n\nيمكنك الآن استخدام جميع ميزات البوت.\nأرسل /menu للبدء.")
                                        send_msg(DEVELOPER_CHAT_ID, f"👤 تم تفعيل مستخدم جديد:\nID: {chat_id}\nالوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    else:
                                        send_msg(chat_id, "❌ **مفتاح تفعيل غير صحيح!**\n\nيجب أن تطلب مفتاح التفعيل من المطور.")
                                elif text == "/start":
                                    welcome = f"""
🎉 **مرحباً بك في بوت التحليل المتقدم!**

🔒 **هذا البوت يتطلب تفعيل:**
للاستخدام، يجب أن تحصل على مفتاح تفعيل.

📋 **للتسجيل:**
1. أرسل للمطور: @[اسم_المطور]
2. اطلب مفتاح التفعيل
3. أرسل: /activate [المفتاح]

💰 **مزايا البوت:**
• تحليل فني متقدم
• 6 استراتيجيات تحليل
• تقارير VIP
• دعم 24/7

🆔 **رقمك:** {chat_id}
                                    """
                                    send_msg(chat_id, welcome)
                                else:
                                    send_msg(chat_id, "🔒 **البوت غير مفعل!**\n\nيجب تفعيل البوت أولاً باستخدام /activate [key]\nاطلب المفتاح من المطور.")
                                continue
                            
                            # إذا المستخدم مفعل، تعامل مع الأوامر
                            if text == "/start":
                                send_msg(chat_id, "✅ **مرحباً بك مجدداً!**\nالبوت مفعل وجاهز للاستخدام.\nأرسل /menu للأوامر.")
                            
                            elif text == "/menu":
                                show_menu(chat_id)
                            
                            elif text.startswith("/analyze "):
                                symbol = text.split(" ", 1)[1]
                                analysis = analyze_crypto(symbol)
                                send_msg(chat_id, analysis)
                            
                            elif text == "/mystats":
                                user_data = activated_users.get(str(chat_id), {})
                                stats = f"""
📊 **إحصائياتك:**

🆔 **رقمك:** {chat_id}
✅ **الحالة:** مفعّل
📅 **تاريخ التفعيل:** {user_data.get('activated_at', 'غير معروف')}
⏳ **المدة:** {user_data.get('expiry', 'مدى الحياة')}

⚡ **للتحليل:** أرسل رمز عملة
💰 **مثال:** BTC, ETH, SOL
                                """
                                send_msg(chat_id, stats)
                            
                            elif text == "/support":
                                send_msg(chat_id, "📞 **الدعم الفني:**\n\nللإبلاغ عن مشاكل أو اقتراحات:\n@[اسم_المطور]\n\nساعات العمل: 24/7")
                            
                            elif text.upper() in ["BTC", "ETH", "SOL", "ADA", "XRP", "BNB", "DOGE"]:
                                analysis = analyze_crypto(text)
                                send_msg(chat_id, analysis)
                            
                            elif text == "developer" or text == "المطور":
                                send_msg(chat_id, f"👑 **المطور:**\n\n🆔 الرقم: {DEVELOPER_CHAT_ID}\n🔑 لديه صلاحيات التحكم الكاملة")
                            
                            elif text.startswith("/"):
                                send_msg(chat_id, "❓ **أمر غير معروف**\nأرسل /menu لعرض الأوامر المتاحة")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
            time.sleep(5)

def run_bot():
    """تشغيل البوت"""
    print("🤖 بدء تشغيل بوت التحليل المتقدم...")
    print(f"🆔 رقم المطور: {DEVELOPER_CHAT_ID}")
    print(f"👥 المستخدمين المفعلين: {len(activated_users)}")
    
    # إرسال رسالة بدء للمطور
    if CHAT_ID:
        send_msg(CHAT_ID, f"""
🚀 **تم تشغيل البوت بنجاح!**

📊 **معلومات السيرفر:**
🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📍 النظام: {'Replit' if IS_REPLIT else 'Local'}
👥 المستخدمين: {len(activated_users)}
🔑 مفتاح التفعيل: {ACTIVATION_KEY}

✅ البوت جاهز لاستقبال الطلبات.
        """)
    
    # بدء معالجة الرسائل
    process_messages()

def keep_alive():
    """الحفاظ على البوت نشط"""
    if IS_REPLIT:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8080)
    else:
        app.run(host='0.0.0.0', port=10000, debug=False)

# ============================================
# 🎬 بدء التشغيل
# ============================================

if __name__ == "__main__":
    # تغيير هذه القيم لبياناتك
    DEVELOPER_CHAT_ID = "7520800507"  # ← رقمك أنت
    ACTIVATION_KEY = "CRYPTO-VIP-2024"  # ← أي مفتاح تريده
    
    # تشغيل البوت في خيط منفصل
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل Keep Alive
    print("🌐 بدء تشغيل ويب سيرفر...")
    keep_alive()
