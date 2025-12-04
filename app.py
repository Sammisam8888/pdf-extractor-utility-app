from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"  # replace in production

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
                "User-Agent": "Mozilla/5.0 (compatible; PaperPluck/1.0)"
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
