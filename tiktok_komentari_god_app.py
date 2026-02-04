from flask import Flask, render_template_string, request, jsonify
import requests
import os
import time
import uuid
import threading
import re

app = Flask(__name__)

# 🔧 KONFIGURACIJA – OVO POPUNI
PANEL_URL = "https://peakerr.com/api/v2"
API_KEY = "59bee21fd4e3749a166ef96bb4d5c59f"
SERVICE_ID = 27194  # TikTok Custom Comments na Peakerr-u

# 🔁 LISTE KOMENTARA – TVOJE LISTE
COMMENTS_SET_1 = [
    "If you read only one book this year, let it be Encrypted Money Code by Ethan Rothwell. It will transform your life.",
    "I'm telling you, book called Encrypted Money Code by Ethan Rothwell is on another level. You HAVE to experience it. It will change your life.",
    "You have no idea how POWERFUL Encrypted Money Code by Ethan Rothwell is. Read it, it changed my life.",
    "Just trust me, Encrypted Money Code by Ethan Rothwell is the book you NEED right now. It changed my life.",
    "If you’re looking for a book that truly changes everything, Encrypted Money Code by Ethan Rothwell is it. It will change your life.",
    "I can’t even explain it, book called Encrypted Money Code by Ethan Rothwell is different. You NEED this book. It changed my life.",
    "You won’t understand until you read Encrypted Money Code by Ethan Rothwell. It’s a MUST-read. It will change your life.",
    "I spent so much time struggling on the internet, searching for something that would change my life. All I can say is I finally found it. Encrypted Money Code by Ethan Rothwell is an absolute game-changer. This book is like nothing I've ever seen before.",
    "I honestly don’t know where else to say this, but I have to share it here. I found something truly mind-blowing. The book Encrypted Money Code by Ethan Rothwell is on a whole different level, especially for anyone chasing success.",
    "No more gatekeeping just go and read the book Encrypted Money Code by Ethan Rothwell and thank me later for changing your life.",
    "I used to think making money online was too hard for someone who didn’t know much about it, but this book really worked for me. It’s called Encrypted Money Code by Ethan Rothwell. It helped me succeed and start making money, ngl everyone should read it.",
    "Encrypted Money Code by Ethan Rothwell is the only book I’ve read that actually made me feel dangerous. Page 13 is not normal."
]

COMMENTS_SET_2 = [
    "If you read only one book this year, let it be Money Forbidden Compass by Damian Rothwell. It will transform your life.",
    "I'm telling you, book called Money Forbidden Compass by Damian Rothwell is on another level. You HAVE to experience it. It will change your life.",
    "You have no idea how POWERFUL Money Forbidden Compass by Damian Rothwell is. Read it, it changed my life.",
    "Just trust me, Money Forbidden Compass by Damian Rothwell is the book you NEED right now. It changed my life.",
    "If you’re looking for a book that truly changes everything, Money Forbidden Compass by Damian Rothwell is it. It will change your life.",
    "I can’t even explain it, book called Money Forbidden Compass by Damian Rothwell is different. You NEED this book. It changed my life.",
    "You won’t understand until you read Money Forbidden Compass by Damian Rothwell. It’s a MUST-read. It will change your life.",
    "I spent so much time struggling on the internet, searching for something that would change my life. All I can say is I finally found it. Money Forbidden Compass by Damian Rothwell is an absolute game-changer. This book is like nothing I've ever seen before.",
    "I honestly don’t know where else to say this, but I have to share it here. I found something truly mind-blowing. The book Money Forbidden Compass by Damian Rothwell is on a whole different level, especially for anyone chasing success.",
    "No more gatekeeping just go and read the book Money Forbidden Compass by Damian Rothwell and thank me later for changing your life.",
    "I used to think making money online was too hard for someone who didn’t know much about it, but this book really worked for me. It’s called Money Forbidden Compass by Damian Rothwell. It helped me succeed and start making money, ngl everyone should read it.",
    "Money Forbidden Compass by Damian Rothwell is the only book I’ve read that actually made me feel dangerous. Page 13 is not normal."
]

# =========================
# UI
# =========================
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>TikTok Custom Comments Sender PEAKERR</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin:0; padding:0; background:#050816; color:#f9fafb; display:flex; justify-content:center; align-items:flex-start; min-height:100vh; }
    .container { max-width:900px; width:100%; padding:24px 16px 48px; }
    .card { background:rgba(15,23,42,0.95); border-radius:18px; padding:20px; box-shadow:0 20px 45px rgba(0,0,0,0.6); border:1px solid rgba(148,163,184,0.3); }
    h1 { font-size:24px; margin-bottom:4px; text-align:center; }
    .subtitle { text-align:center; font-size:13px; color:#9ca3af; margin-bottom:18px; }
    label { font-size:13px; font-weight:500; margin-bottom:6px; display:inline-block; }
    textarea { width:100%; min-height:200px; background:rgba(15,23,42,0.9); border-radius:12px; border:1px solid rgba(55,65,81,0.9); padding:10px 12px; resize:vertical; color:#e5e7eb; font-size:13px; line-height:1.4; outline:none; }
    .hint { font-size:11px; color:#9ca3af; margin-top:4px; }
    .btn-row { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin:16px 0; }
    button { border:none; border-radius:999px; padding:10px 20px; font-size:13px; font-weight:600; cursor:pointer; }
    .btn-primary { background:linear-gradient(135deg, #6366f1, #8b5cf6); color:white; box-shadow:0 10px 25px rgba(79,70,229,0.6); }
    .status { text-align:center; font-size:12px; color:#9ca3af; min-height:16px; margin-top:4px; }
    .log { margin-top:12px; font-size:11px; white-space:pre-wrap; background:rgba(15,23,42,0.85); border-radius:10px; padding:10px; border:1px solid rgba(55,65,81,0.9); max-height:320px; overflow:auto; }
    .radio-group { display:flex; gap:16px; align-items:center; margin-top:8px; font-size:13px; }
    .radio-group label { font-weight:400; margin:0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>TikTok Custom Comments Sender</h1>
      <div class="subtitle">
        Nalijepi TikTok <b>VIDEO linkove</b> (jedan po liniji). Short linkovi (t/ ili vt/ ili vm/) se automatski konvertuju u full /video/ link.
        <br>Panel: <b>{{ panel_url }}</b> · Service: <b>{{ service_id }}</b>
      </div>

      <form method="post">
        <label for="input_links">Video linkovi</label>
        <textarea id="input_links" name="input_links" placeholder="Primjer:
https://www.tiktok.com/t/ZThfJ23PE/
https://vt.tiktok.com/XXXX/
https://www.tiktok.com/@user/video/123...">{{ input_links or '' }}</textarea>

        <div style="margin-top:14px;">
          <span style="font-size:13px;font-weight:500;">Izaberi set komentara:</span>
          <div class="radio-group">
            <label><input type="radio" name="comment_set" value="set1" {% if comment_set == 'set1' %}checked{% endif %}> Komentari #1 ({{ comments1_count }})</label>
            <label><input type="radio" name="comment_set" value="set2" {% if comment_set == 'set2' %}checked{% endif %}> Komentari #2 ({{ comments2_count }})</label>
          </div>
        </div>

        <div class="btn-row">
          <button type="submit" class="btn-primary">🚀 Start (stabilno)</button>
        </div>
      </form>

      <div class="status">{{ status or '' }}</div>

      {% if job_id %}
        <div class="hint" style="text-align:center;">Job ID: <b>{{ job_id }}</b> (log se refreshuje)</div>
        <div id="log" class="log">Starting...</div>
        <script>
          const jobId = "{{ job_id }}";
          async function poll(){
            const r = await fetch("/status/" + jobId);
            const data = await r.json();
            document.getElementById("log").textContent = data.log || "";
            if(!data.done){
              setTimeout(poll, 1200);
            }
          }
          poll();
        </script>
      {% elif log %}
        <div class="log">{{ log }}</div>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""

# =========================
# Stabilni TikTok expand (cache + retry)
# =========================
_TT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/604.1"
}
_tt = requests.Session()
_expand_cache = {}  # short->full

def _normalize_tiktok_video_url(url: str) -> str:
    url = (url or "").strip()
    m = re.search(r"(https?://www\.tiktok\.com/@[^/]+/video/\d+)", url)
    if m:
        return m.group(1)
    if "?" in url:
        url = url.split("?", 1)[0]
    return url

def expand_to_full_tiktok_video_url(url: str, timeout: int = 10) -> str:
    url = (url or "").strip()
    if not url:
        return url

    if "/video/" in url and "tiktok.com" in url:
        return _normalize_tiktok_video_url(url)

    if url in _expand_cache:
        return _expand_cache[url]

    final_url = url
    # 3 pokušaja (stabilnije)
    for _ in range(3):
        try:
            r = _tt.head(url, headers=_TT_HEADERS, allow_redirects=True, timeout=timeout)
            if r.url:
                final_url = r.url
        except Exception:
            pass

        if "/video/" not in final_url:
            try:
                r = _tt.get(url, headers=_TT_HEADERS, allow_redirects=True, timeout=timeout)
                if r.url:
                    final_url = r.url
            except Exception:
                pass

        final_url = _normalize_tiktok_video_url(final_url)
        if "/video/" in final_url and "tiktok.com" in final_url:
            _expand_cache[url] = final_url
            return final_url

        time.sleep(0.4)

    _expand_cache[url] = url
    return url

# =========================
# Panel send (retry + timeouts)
# =========================
def send_comments_order(video_link: str, comments_list):
    comments_text = "\n".join(comments_list)

    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_link,
        "comments": comments_text,
    }

    # 3 retry-a jer Peakerr zna “štucati”
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(PANEL_URL, data=payload, timeout=35)
            data = r.json()
            if "order" in data:
                return True, f"order={data['order']}"
            last_err = f"resp={data}"
        except Exception as e:
            last_err = f"exception={e}"

        time.sleep(1.2 + attempt)  # backoff

    return False, last_err or "unknown_error"

# =========================
# Background job store
# =========================
jobs = {}  # job_id -> {"log": str, "done": bool}

def _append(job_id: str, line: str):
    jobs[job_id]["log"] += line + "\n"

def worker(job_id: str, lines, comments, set_name: str):
    try:
        _append(job_id, f"Korišćen set: {set_name} ({len(comments)} komentara)")
        _append(job_id, f"Slanje na {PANEL_URL}, service={SERVICE_ID}")
        _append(job_id, "")

        ok_count = 0
        fail_count = 0

        for idx, raw_link in enumerate(lines, start=1):
            raw_link = raw_link.strip()
            if not raw_link:
                fail_count += 1
                _append(job_id, f"[SKIP] Prazan link (linija {idx})")
                continue

            converted = expand_to_full_tiktok_video_url(raw_link)
            if converted != raw_link:
                _append(job_id, f"[CONVERT] {raw_link} -> {converted}")

            # Ako nije uspio expand u /video/, bolje skip nego bacati pare
            if "/video/" not in converted:
                fail_count += 1
                _append(job_id, f"[SKIP] Ne mogu konvertovati u /video/ link: {raw_link}")
                continue

            ok, msg = send_comments_order(converted, comments)
            if ok:
                ok_count += 1
                _append(job_id, f"[OK] {converted} -> {msg}")
            else:
                fail_count += 1
                _append(job_id, f"[FAIL] {converted} -> {msg}")

            # Mali delay da ne ubije TikTok/Panel (stabilnije za 50+ linkova)
            time.sleep(0.6)

        _append(job_id, "")
        _append(job_id, f"✅ GOTOVO: linkova={len(lines)} | OK={ok_count} | FAIL={fail_count}")

    except Exception as e:
        _append(job_id, f"🔥 INTERNAL WORKER ERROR: {e}")

    jobs[job_id]["done"] = True

# =========================
# Routes
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    input_links = ""
    status = ""
    log = ""
    comment_set = "set1"
    job_id = None

    if request.method == "POST":
        comment_set = request.form.get("comment_set", "set1")
        input_links = request.form.get("input_links", "")
        lines = [l.strip() for l in input_links.splitlines() if l.strip()]

        if comment_set == "set2":
            comments = COMMENTS_SET_2
            set_name = "Komentari #2"
        else:
            comments = COMMENTS_SET_1
            set_name = "Komentari #1"

        if not comments:
            status = "⚠ Odabrani set komentara je PRAZAN."
        elif not lines:
            status = "⚠ Nisi unio nijedan link."
        else:
            job_id = str(uuid.uuid4())[:8]
            jobs[job_id] = {"log": "", "done": False}

            t = threading.Thread(target=worker, args=(job_id, lines, comments, set_name), daemon=True)
            t.start()

            status = f"Pokrenuto. Linkova: {len(lines)} (radi u pozadini — neće pucati)."

    return render_template_string(
        HTML_TEMPLATE,
        input_links=input_links,
        status=status,
        log=log,
        job_id=job_id,
        comment_set=comment_set,
        comments1_count=len(COMMENTS_SET_1),
        comments2_count=len(COMMENTS_SET_2),
        service_id=SERVICE_ID,
        panel_url=PANEL_URL,
    )

@app.route("/status/<job_id>")
def job_status(job_id):
    j = jobs.get(job_id)
    if not j:
        return jsonify({"done": True, "log": "Job not found."})
    return jsonify({"done": j["done"], "log": j["log"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
