from flask import Flask, render_template_string, request
import requests, os, time, re

app = Flask(__name__)

PANEL_URL = "https://peakerr.com/api/v2"
API_KEY = "59bee21fd4e3749a166ef96bb4d5c59f"
SERVICE_ID = 27194

COMMENTS_SET_1 = [
    "Find the book Encrypted Money Code by Ethan Rothwell. Whoever finds this book will have an unfair advantage in how to make money and be successful in life. Trust me on this one.",
"Why is no one talking about Encrypted Money Code by Ethan Rothwell? This book completely changed my perception of money and how we’re actually being controlled.",
"I spent so much time struggling on the internet, searching for something that would change my life. All I can say is I finally found it. Encrypted Money Code by Ethan Rothwell is an absolute game-changer. This book is like nothing I’ve ever seen before.",
"I used to think making money online was too hard for someone who didn’t know much about it, but this book actually worked for me. It’s called Encrypted Money Code by Ethan Rothwell. It helped me start making money — ngl, everyone should read it.",
"Encrypted Money Code by Ethan Rothwell is the only book I’ve read that actually made me feel “dangerous” in a good way. Page 13 is not normal.",
"I know it’s cliché to recommend books through comments and say “it changed my life,” but I have to recommend this one: Encrypted Money Code by Ethan Rothwell. There’s insane hidden information in there.",
"Plot twist — you seeing this comment about Encrypted Money Code by Ethan Rothwell isn’t random. Nothing is.",
"No influencer, no coach, no “guru” ever hit me the way Encrypted Money Code by Ethan Rothwell did. It’s raw, uncomfortable, and it forces you to see how the world really works.",
"If you read only one book this year, let it be Encrypted Money Code by Ethan Rothwell. It will transform the way you look at money and success.",
"I’m telling you, the book Encrypted Money Code by Ethan Rothwell is on another level. You HAVE to experience it. It will change your life.",
"They banned Encrypted Money Code by Ethan Rothwell for a reason. I suggest y’all read it ASAP.",
]

COMMENTS_SET_2 = [
    "If you read only one book this year, let it be Money Forbidden Compass by Damian Rothwell. It will transform your life.",
    "I'm telling you, book called Money Forbidden Compass by Damian Rothwell is on another level. You HAVE to experience it. It will change your life.",
    "You have no idea how POWERFUL Money Forbidden Compass by Damian Rothwell is. Read it, it changed my life.",
    "Just trust me, Money Forbidden Compass by Damian Rothwell is the book you NEED right now. It changed my life.",
]

# ✅ da ne puca kad zalijepiš puno linkova
MAX_LINKS_PER_RUN = 8
DELAY_BETWEEN = 0.7
REQUEST_TIMEOUT = 30

HTML = """
<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Peakerr TikTok Custom Comments</title>
<style>
body{background:#050816;color:#fff;font-family:system-ui;margin:0;padding:20px}
.card{max-width:900px;margin:0 auto;background:rgba(15,23,42,.95);padding:18px;border-radius:14px;border:1px solid rgba(148,163,184,.25)}
textarea{width:100%;min-height:210px;background:rgba(15,23,42,.9);color:#e5e7eb;border:1px solid rgba(55,65,81,.9);border-radius:10px;padding:10px}
button{margin-top:10px;border:0;border-radius:999px;padding:10px 16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:700;cursor:pointer}
small{color:#9ca3af}
pre{white-space:pre-wrap;background:rgba(15,23,42,.85);padding:10px;border-radius:10px;border:1px solid rgba(55,65,81,.9);max-height:320px;overflow:auto}
</style></head><body>
<div class="card">
<h2 style="text-align:center;margin:0 0 8px">TikTok Custom Comments (Peakerr)</h2>
<small>Short linkovi (t/vt/vm) se automatski pretvaraju u full /video/ link. Limit po run-u: <b>{{ maxn }}</b></small>
<form method="post">
<div style="margin-top:10px">
<label><input type="radio" name="set" value="1" {% if setsel=='1' %}checked{% endif %}> Encrypted</label>
<label style="margin-left:12px"><input type="radio" name="set" value="2" {% if setsel=='2' %}checked{% endif %}> Compass</label>
</div>
<textarea name="links" placeholder="1 link po liniji...">{{ links or '' }}</textarea>
<button type="submit">Send</button>
</form>
{% if status %}<p><b>{{ status }}</b></p>{% endif %}
{% if log %}<pre>{{ log }}</pre>{% endif %}
</div></body></html>
"""

_tt = requests.Session()
_TT_HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}

def normalize_video(url: str) -> str:
    url = (url or "").strip()
    m = re.search(r"(https?://www\.tiktok\.com/@[^/]+/video/\d+)", url)
    if m:
        return m.group(1)
    if "?" in url:
        url = url.split("?", 1)[0]
    return url

def expand_link(url: str) -> str:
    url = (url or "").strip()
    if "/video/" in url:
        return normalize_video(url)
    # 2 pokušaja (dovoljno a kratko)
    for _ in range(2):
        try:
            r = _tt.head(url, headers=_TT_HEADERS, allow_redirects=True, timeout=10)
            if r.url and "/video/" in r.url:
                return normalize_video(r.url)
        except Exception:
            pass
        try:
            r = _tt.get(url, headers=_TT_HEADERS, allow_redirects=True, timeout=10)
            if r.url and "/video/" in r.url:
                return normalize_video(r.url)
        except Exception:
            pass
        time.sleep(0.3)
    return url

def send_order(video_link: str, comments_list):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_link,
        "comments": "\n".join(comments_list)
    }
    # 2 retry
    last = None
    for attempt in range(2):
        try:
            r = requests.post(PANEL_URL, data=payload, timeout=REQUEST_TIMEOUT)
            data = r.json()
            if "order" in data:
                return True, f"order={data['order']}"
            last = f"resp={data}"
        except Exception as e:
            last = f"exception={e}"
        time.sleep(0.6 + attempt)
    return False, last or "error"

@app.route("/", methods=["GET","POST"])
def index():
    links = ""
    log_lines = []
    status = ""
    setsel = "1"

    if request.method == "POST":
        setsel = request.form.get("set","1")
        links = request.form.get("links","")
        raw_lines = [l.strip() for l in links.splitlines() if l.strip()]

        if setsel == "2":
            comments = COMMENTS_SET_2
        else:
            comments = COMMENTS_SET_1

        # ✅ limit da ne puca
        total = len(raw_lines)
        use = raw_lines[:MAX_LINKS_PER_RUN]
        skipped = max(0, total - len(use))

        okc = 0
        failc = 0

        for raw in use:
            full = expand_link(raw)
            if full != raw:
                log_lines.append(f"[CONVERT] {raw} -> {full}")

            if "/video/" not in full:
                failc += 1
                log_lines.append(f"[SKIP] Ne mogu dobiti /video/ link: {raw}")
                continue

            ok, msg = send_order(full, comments)
            if ok:
                okc += 1
                log_lines.append(f"[OK] {full} -> {msg}")
            else:
                failc += 1
                log_lines.append(f"[FAIL] {full} -> {msg}")

            time.sleep(DELAY_BETWEEN)

        status = f"Done. Total={total} | Sent={len(use)} | OK={okc} | FAIL={failc} | Skipped={skipped} (limit {MAX_LINKS_PER_RUN})"

    return render_template_string(
        HTML,
        links=links,
        log="\n".join(log_lines),
        status=status,
        setsel=setsel,
        maxn=MAX_LINKS_PER_RUN
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

