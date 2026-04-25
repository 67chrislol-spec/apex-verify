import os
import requests
from flask import Flask, request, render_template_string, redirect, session
import secrets

app = Flask(**name**)
app.secret_key = secrets.token_hex(32)

CLIENT_ID = “1496753618861424700”
CLIENT_SECRET = os.environ.get(“CLIENT_SECRET”)
BOT_TOKEN = os.environ.get(“BOT_TOKEN”)
GUILD_ID = “1488422873415811092”
ROLE_NAME = “apex | member”
REDIRECT_URI = os.environ.get(“REDIRECT_URI”)

DISCORD_API = “https://discord.com/api/v10”

HTML = “””<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>APEX Verification</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--orange:#ff5a1e;--bg:#0a0a0b;--surface:#111113;--border:rgba(255,255,255,0.07);--text:#f0ede8;--muted:#888}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;display:flex;align-items:center;justify-content:center}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:48px 48px;mask-image:radial-gradient(ellipse 70% 70% at 50% 50%,black 40%,transparent 100%);pointer-events:none;z-index:0}
body::after{content:'';position:fixed;width:600px;height:600px;background:radial-gradient(circle,rgba(255,90,30,0.12) 0%,transparent 70%);top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:0}
.card{position:relative;z-index:1;background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:52px 48px 44px;width:min(480px,calc(100vw - 32px));text-align:center;box-shadow:0 32px 80px rgba(0,0,0,0.6);animation:rise 0.6s cubic-bezier(0.22,1,0.36,1) both}
@keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
.icon{width:72px;height:72px;border-radius:50%;background:rgba(255,90,30,0.15);border:1.5px solid rgba(255,90,30,0.4);display:flex;align-items:center;justify-content:center;margin:0 auto 28px;font-size:32px;box-shadow:0 0 28px rgba(255,90,30,0.4)}
h1{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.08em;margin-bottom:12px}
.subtitle{color:var(--muted);font-size:0.95rem;margin-bottom:32px;line-height:1.6}
.btn{display:inline-block;background:var(--orange);color:#fff;border:none;border-radius:12px;font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:500;padding:16px 40px;cursor:pointer;width:100%;box-shadow:0 0 24px rgba(255,90,30,0.35);transition:all 0.2s;text-decoration:none}
.btn:hover{background:#ff6e37;box-shadow:0 0 36px rgba(255,90,30,0.55);transform:translateY(-1px)}
.success{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#4ade80;border-radius:12px;padding:14px 18px;margin-bottom:24px}
.error{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#f87171;border-radius:12px;padding:14px 18px;margin-bottom:24px}
.avatar{width:64px;height:64px;border-radius:50%;border:2px solid var(--orange);margin:0 auto 16px;display:block}
.footer{margin-top:24px;color:var(--muted);font-size:0.78rem}
</style>
</head>
<body>
<div class="card">
  <div class="icon">{{ icon }}</div>
  <h1>{{ title }}</h1>
  {% if avatar %}
  <img class="avatar" src="{{ avatar }}" alt="avatar"/>
  {% endif %}
  <p class="subtitle">{{ subtitle }}</p>
  {% if status == "success" %}<div class="success">{{ message }}</div>{% endif %}
  {% if status == "error" %}<div class="error">{{ message }}</div>{% endif %}
  {% if show_button %}
  <form method="POST" action="/do_verify">
    <button class="btn" type="submit">Verify Me</button>
  </form>
  {% endif %}
  <p class="footer">APEX Verification System</p>
</div>
</body>
</html>"""

def render(icon, title, subtitle, status=None, message=None, show_button=False, avatar=None):
return render_template_string(HTML, icon=icon, title=title, subtitle=subtitle,
status=status, message=message, show_button=show_button, avatar=avatar)

@app.route(”/”)
def index():
return render(“lightning”, “APEX Verify”, “Use the Verify button in the Discord server to get started.”)

@app.route(”/callback”)
def callback():
code = request.args.get(“code”)
error = request.args.get(“error”)

```
if error or not code:
    return render("X", "Access Denied", "You declined the verification.", status="error", message="Verification was cancelled.")

token_res = requests.post(
    DISCORD_API + "/oauth2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

if token_res.status_code != 200:
    return render("X", "Error", "Something went wrong.", status="error", message="Could not exchange code. Try clicking Verify again.")

access_token = token_res.json().get("access_token")

user_res = requests.get(DISCORD_API + "/users/@me", headers={"Authorization": "Bearer " + access_token})
if user_res.status_code != 200:
    return render("X", "Error", "Could not fetch your account.", status="error", message="Please try again.")

user = user_res.json()
session["user_id"] = user["id"]
session["username"] = user.get("global_name") or user.get("username", "Member")
avatar_hash = user.get("avatar")
if avatar_hash:
    session["avatar"] = "https://cdn.discordapp.com/avatars/" + user["id"] + "/" + avatar_hash + ".png"
else:
    session["avatar"] = None

return render(
    "lightning",
    "Welcome, " + session["username"] + "!",
    "You are logged in with Discord. Click below to complete your verification.",
    show_button=True,
    avatar=session.get("avatar"),
)
```

@app.route(”/do_verify”, methods=[“POST”])
def do_verify():
user_id = session.get(“user_id”)
username = session.get(“username”, “Member”)
avatar = session.get(“avatar”)

```
if not user_id:
    return render("X", "Session Expired", "Please try again.", status="error", message="Go back to Discord and click Verify again.")

roles_res = requests.get(DISCORD_API + "/guilds/" + GUILD_ID + "/roles", headers={"Authorization": "Bot " + BOT_TOKEN})
role_id = None
unverified_id = None
for role in roles_res.json():
    if role["name"].strip().lower() == "apex | member":
        role_id = role["id"]
    if role["name"].strip().lower() == "unverified":
        unverified_id = role["id"]

if not role_id:
    return render("X", "Error", "Role not found.", status="error", message="Contact an admin.", avatar=avatar)

member_res = requests.get(DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id, headers={"Authorization": "Bot " + BOT_TOKEN})

if member_res.status_code != 200:
    return render("X", "Not in Server", "Join the server first.", status="error", message="Join APEX then try again.", avatar=avatar)

member_data = member_res.json()

if role_id in member_data.get("roles", []):
    return render("V", "Already Verified", "You already have access.", status="success", message="You are already verified! Head back to Discord.", avatar=avatar)

add_res = requests.put(
    DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id + "/roles/" + role_id,
    headers={"Authorization": "Bot " + BOT_TOKEN}
)

if unverified_id and unverified_id in member_data.get("roles", []):
    requests.delete(DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id + "/roles/" + unverified_id, headers={"Authorization": "Bot " + BOT_TOKEN})

if add_res.status_code in (200, 204):
    session.clear()
    return render("V", "Verified!", "Welcome to APEX, " + username + ".", status="success", message="You now have full access. Head back to Discord!", avatar=avatar)
else:
    return render("X", "Error", "Could not assign role.", status="error", message="Bot may be missing permissions. Contact an admin.", avatar=avatar)
```

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port)
