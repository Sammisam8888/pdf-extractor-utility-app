from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import re
from urllib.parse import urlparse, unquote
import threading
import time
import os
from flask import Response, stream_with_context

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Render URL to ping
RENDER_URL = os.getenv("RENDER_URL", "https://pdf-extractor-app-pdeb.onrender.com")

def keep_alive():
    """
    Ping the Render instance every 14 minutes 50 seconds (890 seconds)
    so that it never sleeps.
    """
    while True:
        try:
            print("Heartbeat: Pinging Render...")
            requests.get(RENDER_URL, timeout=10)
            print("Heartbeat: Ping successful")
        except Exception as e:
            print(f"Heartbeat error: {e}")
        
        time.sleep(890)  # 14 minutes 50 seconds


# regex to find sitepdfs URL in page HTML
SITEPDFS_RE = re.compile(r'(https?://www\.selfstudys\.com/sitepdfs/[A-Za-z0-9_-]+)')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        page_url = request.form.get("page_url", "").strip()
        if not page_url:
            flash("Please paste a SelfStudys page URL.", "warning")
            return redirect(url_for("index"))

        # Basic validation: only accept selfstudys domain (helps teacher safety)
        parsed = urlparse(page_url)
        if "selfstudys.com" not in (parsed.netloc or ""):
            flash("Please provide a URL from selfstudys.com.", "danger")
            return redirect(url_for("index"))

        try:
            # Fetch the page
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; PDF Extractor/1.0)"
            }
            resp = requests.get(page_url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text

            # Search for the sitepdfs link
            m = SITEPDFS_RE.search(html)
            if not m:
                flash("Couldn't find a sitepdfs link on that page. Try the page in a browser, then paste the same URL here.", "danger")
                return redirect(url_for("index"))

            pdf_url = m.group(1)

            # Normalize to full https
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url

            # Render viewer page and pass the pdf_url
            return render_template("viewer.html", pdf_url=pdf_url, source_page=page_url)

        except requests.RequestException as e:
            flash(f"Network error: {e}", "danger")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/download")
def download_pdf():
    pdf_url = request.args.get("url")
    if not pdf_url:
        return "Missing URL", 400

    # Basic validation to ensure we are only proxying selfstudys PDFs
    # (Optional but good for security)
    if "selfstudys.com" not in pdf_url:
         return "Invalid URL domain", 403

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; PDF Extractor/1.0)"
        }
        req = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
        req.raise_for_status()

        # Extract filename from URL
        filename = pdf_url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        return Response(
            stream_with_context(req.iter_content(chunk_size=1024)),
            content_type=req.headers.get("Content-Type", "application/pdf"),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except requests.RequestException as e:
        return f"Error downloading PDF: {e}", 500



if __name__ == "__main__":
    # Start heartbeat thread
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(debug=True, port=5000)
