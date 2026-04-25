import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

CLIENT_ID = "1496753618861424700"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GUILD_ID = "1488422873415811092"
ROLE_NAME = "apex | member"
REDIRECT_URI = os.environ.get("REDIRECT_URI")

DISCORD_API = "https://discord.com/api/v10"

HTML = """<!DOCTYPE html>
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
.card{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:52px 48px 44px;width:min(480px,calc(100vw - 32px));text-align:center}
.icon{width:72px;height:72px;border-radius:50%;background:rgba(255,90,30,0.15);border:1.5px solid rgba(255,90,30,0.4);display:flex;align-items:center;justify-content:center;margin:0 auto 28px;font-size:32px}
h1{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.08em;margin-bottom:12px}
.subtitle{color:var(--muted);font-size:0.95rem;margin-bottom:32px}
.success{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#4ade80;border-radius:12px;padding:14px 18px;margin-bottom:24px}
.error{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#f87171;border-radius:12px;padding:14px 18px;margin-bottom:24px}
.footer{margin-top:24px;color:var(--muted);font-size:0.78rem}
</style>
</head>
<body>
<div class="card">
  <div class="icon">{{ icon }}</div>
  <h1>{{ title }}</h1>
  <p class="subtitle">{{ subtitle }}</p>
  {% if status == "success" %}<div class="success">{{ message }}</div>{% endif %}
  {% if status == "error" %}<div class="error">{{ message }}</div>{% endif %}
  <p class="footer">APEX Verification System</p>
</div>
</body>
</html>"""


def render(icon, title, subtitle, status=None, message=None):
    return render_template_string(HTML, icon=icon, title=title, subtitle=subtitle, status=status, message=message)


@app.route("/")
def index():
    return render("lightning", "APEX Verify", "Use the link from your Discord server to verify.")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")

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
        return render("X", "Error", "Something went wrong.", status="error", message="Could not exchange code. Try again.")

    access_token = token_res.json().get("access_token")

    user_res = requests.get(DISCORD_API + "/users/@me", headers={"Authorization": "Bearer " + access_token})
    if user_res.status_code != 200:
        return render("X", "Error", "Could not fetch your account.", status="error", message="Please try again.")

    user = user_res.json()
    user_id = user["id"]
    username = user.get("global_name") or user.get("username", "Member")

    roles_res = requests.get(DISCORD_API + "/guilds/" + GUILD_ID + "/roles", headers={"Authorization": "Bot " + BOT_TOKEN})
    role_id = None
    unverified_id = None
    for role in roles_res.json():
        if role["name"].strip().lower() == "apex | member":
            role_id = role["id"]
        if role["name"].strip().lower() == "unverified":
            unverified_id = role["id"]

    if not role_id:
        return render("X", "Error", "Role not found.", status="error", message="Contact an admin.")

    member_res = requests.get(DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id, headers={"Authorization": "Bot " + BOT_TOKEN})

    if member_res.status_code != 200:
        return render("X", "Not in Server", "Join the server first.", status="error", message="Join APEX then try again.")

    member_data = member_res.json()

    if role_id in member_data.get("roles", []):
        return render("V", "Already Verified", "You already have access.", status="success", message="You are already verified! Head back to Discord.")

    requests.put(DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id + "/roles/" + role_id, headers={"Authorization": "Bot " + BOT_TOKEN})

    if unverified_id and unverified_id in member_data.get("roles", []):
        requests.delete(DISCORD_API + "/guilds/" + GUILD_ID + "/members/" + user_id + "/roles/" + unverified_id, headers={"Authorization": "Bot " + BOT_TOKEN})

    return render("V", "Verified!", "Welcome to APEX, " + username + ".", status="success", message="You now have full access. Head back to Discord!")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
