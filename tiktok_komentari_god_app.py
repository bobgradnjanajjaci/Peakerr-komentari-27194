from flask import Flask, render_template_string, request
import requests, os, time, re

app = Flask(__name__)

PANEL_URL = "https://peakerr.com/api/v2"
API_KEY = "59bee21fd4e3749a166ef96bb4d5c59f"
SERVICE_ID = 27194

# ✅ SET 1 – Encrypted Money Code (tvoja lista)
COMMENTS_SET_1 = [
    "Find the book Encrypted Money Code by Ethan Rothwell. Whoever finds this book will have an unfair advantage in how to make money and be successful in life. Trust me on this one.",
    "Why is no one talking about Encrypted Money Code by Ethan Rothwell? This book completely changed my perception of money and how we’re actually being controlled.",
    "I spent so much time struggling on the internet, searching for something that would change my life. All I can say is I finally found it. Encrypted Money Code by Ethan Rothwell is an absolute game-changer. This book is like nothing I’ve ever seen before.",
    "I used to think making money online was too hard for someone who didn’t know much about it, but this book actually worked for me. It’s called Encrypted Money Code by Ethan Rothwell. It helped me start making money — ngl, everyone should read it.",
    "Encrypted Money Code by Ethan Rothwell is the only book I’ve read that actually made me feel dangerous in a good way. Page 13 is not normal.",
    "I know it’s cliché to recommend books through comments and say it changed my life, but I have to recommend this one: Encrypted Money Code by Ethan Rothwell. There’s insane hidden information in there.",
    "Plot twist — you seeing this comment about Encrypted Money Code by Ethan Rothwell isn’t random. Nothing is.",
    "No influencer, no coach, no guru ever hit me the way Encrypted Money Code by Ethan Rothwell did. It’s raw, uncomfortable, and it forces you to see how the world really works.",
    "If you read only one book this year, let it be Encrypted Money Code by Ethan Rothwell. It will transform the way you look at money and success.",
    "I’m telling you, the book Encrypted Money Code by Ethan Rothwell is on another level. You HAVE to experience it. It will change your life.",
    "They banned Encrypted Money Code by Ethan Rothwell for a reason. I suggest y’all read it ASAP."
]

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Peakerr TikTok Custom Comments</title>
<style>
body{background:#050816;color:#fff;font-family:system-ui;margin:0;padding:20px}
.card{max-width:900px;margin:0 auto;background:rgba(15,23,42,.95);padding:18px;border-radius:14px;border:1px solid rgba(148,163,184,.25)}
textarea{width:100%;min-height:210px;background:rgba(15,23,42,.9);color:#e5e7eb;border:1px solid rgba(55,65,81,.9);border-radius:10px;padding:10px}
button{margin-top:10px;border:0;border-radius:999px;padding:10px 16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:700;cursor:pointer}
pre{white-space:pre-wrap;background:rgba(15,23,42,.85);padding:10px;border-radius:10px;border:1px solid rgba(55,65,81,.9);max-height:320px;overflow:auto}
</style>
</head>
<body>
<div class="card">
<h2 style="text-align:center;margin:0 0 8px">TikTok Custom Comments (Peakerr)</h2>
<form method="post">
<textarea name="links" placeholder="Nalijepi TikTok video linkove (1 po liniji)">{{ links or '' }}</textarea>
<button type="submit">Send</button>
</form>
{% if status %}<p><b>{{ status }}</b></p>{% endif %}
{% if log %}<pre>{{ log }}</pre>{% endif %}
</div>
</body>
</html>
"""

_session = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}

def expand_link(url: str) -> str:
    url = (url or "").strip()
    if "/video/" in url:
        return url.split("?")[0]
    try:
        r = _session.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if r.url:
            return r.url.split("?")[0]
    except:
        pass
    try:
        r = _session.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if r.url:
            return r.url.split("?")[0]
    except:
        pass
    return url

def send_order(video_link: str, comments_list):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_link,
        "comments": "\n".join(comments_list)
    }
    try:
        r = requests.post(PANEL_URL, data=payload, timeout=30)
        data = r.json()
        if "order" in data:
            return True, f"order={data['order']}"
        return False, str(data)
    except Exception as e:
        return False, str(e)

@app.route("/", methods=["GET","POST"])
def index():
    links = ""
    log_lines = []
    status = ""

    if request.method == "POST":
        links = request.form.get("links","")
        raw_lines = [l.strip() for l in links.splitlines() if l.strip()]

        okc = 0
        failc = 0

        for raw in raw_lines:
            full = expand_link(raw)
            ok, msg = send_order(full, COMMENTS_SET_1)
            if ok:
                okc += 1
                log_lines.append(f"[OK] {full} -> {msg}")
            else:
                failc += 1
                log_lines.append(f"[FAIL] {full} -> {msg}")
            time.sleep(0.6)  # mali delay da Peakerr ne blokira

        status = f"Gotovo. Ukupno: {len(raw_lines)}, OK: {okc}, FAIL: {failc}"

    return render_template_string(HTML, links=links, log="\n".join(log_lines), status=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
