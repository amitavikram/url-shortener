from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import random
import string
from urllib.parse import urlparse
import requests
import re

app = Flask(__name__)

DATABASE = "urls.db"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db():
    return sqlite3.connect(DATABASE)


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# WEBSITE VALIDATION
# --------------------------------------------------

def website_exists(url):
    try:
        response = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                )
            },
            allow_redirects=True
        )

        # Reject HTTP error responses
        if response.status_code >= 400:
            return False

        # Check that the response is a webpage
        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if (
            "text/html" not in content_type
            and "application/xhtml+xml" not in content_type
        ):
            return False

        # Check final URL after redirects
        final_url = response.url

        if not final_url:
            return False

        # Get HTML
        html = response.text.lower()

        # Remove excessive whitespace
        clean_html = re.sub(
            r"\s+",
            " ",
            html
        )

        # Common indicators of a missing page
        not_found_phrases = [
            "404 not found",
            "page not found",
            "page doesn't exist",
            "page does not exist",
            "page cannot be found",
            "page could not be found",
            "this page doesn't exist",
            "this page does not exist",
            "content not found",
            "resource not found",
            "url not found",
            "requested page was not found",
            "the page you requested could not be found",
            "the requested page was not found",
            "sorry, we couldn't find",
            "sorry, we could not find",
            "we couldn't find that page",
            "we could not find that page",
            "nothing here",
            "no results found"
        ]

        # Reject obvious not-found pages
        for phrase in not_found_phrases:
            if phrase in clean_html:
                return False

        # Check page title
        title_match = re.search(
            r"<title[^>]*>(.*?)</title>",
            html,
            re.IGNORECASE | re.DOTALL
        )

        title = ""

        if title_match:
            title = re.sub(
                r"\s+",
                " ",
                title_match.group(1)
            ).strip()

        not_found_title_phrases = [
            "404",
            "page not found",
            "not found",
            "error 404",
            "page doesn't exist",
            "page does not exist",
            "content not found"
        ]

        for phrase in not_found_title_phrases:
            if phrase in title:
                return False

        # Remove scripts and styles
        visible_text = re.sub(
            r"<script.*?</script>",
            "",
            html,
            flags=re.IGNORECASE | re.DOTALL
        )

        visible_text = re.sub(
            r"<style.*?</style>",
            "",
            visible_text,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Remove HTML tags
        visible_text = re.sub(
            r"<[^>]+>",
            " ",
            visible_text
        )

        # Clean whitespace
        visible_text = re.sub(
            r"\s+",
            " ",
            visible_text
        ).strip()

        # Reject almost-empty pages
        if len(visible_text) < 20:
            return False

        return True

    except requests.exceptions.Timeout:
        return False

    except requests.exceptions.ConnectionError:
        return False

    except requests.exceptions.RequestException:
        return False

    except Exception:
        return False


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# SHORTEN URL
# --------------------------------------------------

@app.route("/shorten", methods=["POST"])
def shorten():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Invalid request."
        }), 400

    original_url = data.get(
        "url",
        ""
    ).strip()

    # Empty URL
    if not original_url:
        return jsonify({
            "error": "Please enter a URL."
        }), 400

    # URL format validation
    parsed_url = urlparse(
        original_url
    )

    if (
        parsed_url.scheme not in ["http", "https"]
        or not parsed_url.netloc
    ):
        return jsonify({
            "error": "Please enter a valid URL."
        }), 400

    # Check whether webpage exists
    if not website_exists(original_url):
        return jsonify({
            "error": (
                "This webpage does not exist "
                "or cannot be reached."
            )
        }), 400

    # Generate unique short code
    characters = (
        string.ascii_letters +
        string.digits
    )

    while True:

        short_code = "".join(
            random.choice(characters)
            for _ in range(6)
        )

        conn = get_db()

        existing = conn.execute(
            """
            SELECT id
            FROM urls
            WHERE short_code = ?
            """,
            (short_code,)
        ).fetchone()

        conn.close()

        if existing is None:
            break

    # Save URL
    conn = get_db()

    conn.execute(
        """
        INSERT INTO urls
        (
            short_code,
            original_url
        )
        VALUES (?, ?)
        """,
        (
            short_code,
            original_url
        )
    )

    conn.commit()
    conn.close()

    # Create short URL
    short_url = (
        request.host_url +
        short_code
    )

    return jsonify({
        "short_url": short_url
    })


# --------------------------------------------------
# REDIRECT SHORT URL
# --------------------------------------------------

@app.route("/<short_code>")
def redirect_url(short_code):

    conn = get_db()

    result = conn.execute(
        """
        SELECT original_url
        FROM urls
        WHERE short_code = ?
        """,
        (short_code,)
    ).fetchone()

    conn.close()

    if result is None:
        return (
            "Short URL not found",
            404
        )

    return redirect(
        result[0]
    )


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    create_database()

    app.run()