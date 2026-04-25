import os
import requests
from flask import Flask, request, redirect, render_template_string

app = Flask(**name**)

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
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--orange:#ff5a1e;--bg:#0a0a0b;--surface:#111113;--border:rgba(255,255,255,0.07);--text:#f0ede8;--muted:#888}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;display:flex;align-items:center;justify-content:center;overflow:hidden}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:48px 48px;mask-image:radial-gradient(ellipse 70% 70% at 50% 50%,black 40%,transparent 100%);pointer-events:none;z-index:0}
body::after{content:'';position:fixed;width:600px;height:600px;background:radial-gradient(circle,rgba(255,90,30,0.12) 0%,transparent 70%);top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:0}
.card{position:relative;z-index:1;background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:52px 48px 44px;width:min(480px,calc(100vw - 32px));text-align:center;box-shadow:0 0 0 1px rgba(255,255,255,0.03),0 32px 80px rgba(0,0,0,0.6);animation:rise 0.6s cubic-bezier(0.22,1,0.36,1) both}
@keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
.icon{width:72px;height:72px;border-radius:50%;background:rgba(255,90,30,0.15);border:1.5px solid rgba(255,90,30,0.4);display:flex;align-items:center;justify-content:center;margin:0 auto 28px;font-size:32px;box-shadow:0 0 28px rgba(255,90,30,0.4)}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(2rem,6vw,2.8rem);letter-spacing:0.08em;line-height:1;margin-bottom:12px}
.subtitle{color:var(--muted);font-size:0.95rem;font-weight:300;line-height:1.6;margin-bottom:32px}
.success{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#4ade80;border-radius:12px;padding:14px 18px;font-size:0.95rem;font-weight:500;margin-bottom:24px}
.error{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#f87171;border-radius:12px;padding:14px 18px;font-size:0.95rem;font-weight:500;margin-bottom:24px}
.footer{margin-top:24px;color:var(--muted);font-size:0.78rem;line-height:1.5}
</style>
</head>
<body>
<div class="card">
  <div class="icon">{{ icon }}</div>
  <h1>{{ title }}</h1>
  <p class="subtitle">{{ subtitle }}</p>
  {% if status == "success" %}
  <div class="success">{{ message }}</div>
  {% elif status == "error" %}
  <div class="error">{{ message }}</div>
  {% endif %}
  <p class="footer">APEX Verification System</p>
</div>
</body>
</html>"""

def render(icon, title, subtitle, status=None, message=None):
return render_template_string(
HTML, icon=icon, title=title, subtitle=subtitle,
status=status, message=message
)

@app.route(”/”)
def index():
return render(“⚡”, “APEX Verify”, “Use the link from your Discord server to verify.”)

@app.route(”/callback”)
def callback():
code = request.args.get(“code”)
error = request.args.get(“error”)

```
if error or not code:
    return render("❌", "Access Denied", "You declined the verification request.",
                  status="error", message="Verification was cancelled.")

# Exchange code for token
token_res = requests.post(
    f"{DISCORD_API}/oauth2/token",
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
    return render("❌", "Error", "Something went wrong.",
                  status="error", message="Could not exchange code. Please try again.")

access_token = token_res.json().get("access_token")

# Get user info
user_res = requests.get(
    f"{DISCORD_API}/users/@me",
    headers={"Authorization": f"Bearer {access_token}"},
)
if user_res.status_code != 200:
    return render("❌", "Error", "Could not fetch your Discord account.",
                  status="error", message="Please try again.")

user = user_res.json()
user_id = user["id"]
username = user.get("global_name") or user.get("username", "Member")

# Get role ID
roles_res = requests.get(
    f"{DISCORD_API}/guilds/{GUILD_ID}/roles",
    headers={"Authorization": f"Bot {BOT_TOKEN}"},
)
role_id = None
for role in roles_res.json():
    if role["name"].strip().lower() == ROLE_NAME:
        role_id = role["id"]
        break

if not role_id:
    return render("❌", "Error", "Role not found.",
                  status="error", message="The member role could not be found. Contact an admin.")

# Check if already in guild
member_res = requests.get(
    f"{DISCORD_API}/guilds/{GUILD_ID}/members/{user_id}",
    headers={"Authorization": f"Bot {BOT_TOKEN}"},
)

if member_res.status_code == 200:
    member_data = member_res.json()
    if role_id in member_data.get("roles", []):
        return render("✅", "Already Verified", "You already have access to the server.",
                      status="success", message="You are already verified! Head back to Discord.")

    # Add role
    add_res = requests.put(
        f"{DISCORD_API}/guilds/{GUILD_ID}/members/{user_id}/roles/{role_id}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"},
    )

    # Remove unverified role if present
    unverified_id = None
    for role in roles_res.json():
        if role["name"].strip().lower() == "unverified":
            unverified_id = role["id"]
            break
    if unverified_id and unverified_id in member_data.get("roles", []):
        requests.delete(
            f"{DISCORD_API}/guilds/{GUILD_ID}/members/{user_id}/roles/{unverified_id}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )

    if add_res.status_code in (200, 204):
        return render("✅", "Verified!", f"Welcome to APEX, {username}.",
                      status="success", message="You now have full access. Head back to Discord!")
    else:
        return render("❌", "Error", "Could not assign role.",
                      status="error", message="Bot may be missing permissions. Contact an admin.")
else:
    return render("❌", "Not in Server", "You need to join the server first.",
                  status="error", message="Join the APEX Discord server then try verifying again.")
```

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port)
