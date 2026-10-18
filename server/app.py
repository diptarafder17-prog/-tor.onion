#!/usr/bin/env python3
"""
Flask server for Tor-backed UI.

- Serves static files from ../site
- /api/ip          -> returns {"default": "<your-ip>", "tor": "<tor-ip-or-null>"}
- /api/newnym      -> requests Tor to rotate circuits via ControlPort (requires control auth)
Security:
- binds to 127.0.0.1 only by default
- sets secure response headers (CSP, X-Frame-Options, etc.)
"""

import os
import logging
from flask import Flask, jsonify, send_from_directory, request
import requests
from requests.exceptions import RequestException

# Optional: stem for Tor control (recommended)
try:
    from stem import Signal
    from stem.control import Controller
    HAVE_STEM = True
except Exception:
    HAVE_STEM = False

# Config (can be overridden via env)
SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "site")
HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
PORT = int(os.environ.get("FLASK_PORT", "5000"))

# Tor proxy and control configuration
# TOR_SOCKS should be in host:port form (e.g. 127.0.0.1:9050)
TOR_SOCKS = os.environ.get("TOR_SOCKS", "127.0.0.1:9050")
# Use socks5h to force remote DNS resolution through the proxy
TOR_SOCKS_PROXY = {
    "http": f"socks5h://{TOR_SOCKS}",
    "https": f"socks5h://{TOR_SOCKS}",
}

TOR_CONTROL_HOST = os.environ.get("TOR_CONTROL_HOST", "127.0.0.1")
TOR_CONTROL_PORT = int(os.environ.get("TOR_CONTROL_PORT", "9051"))
TOR_CONTROL_PASSWORD = os.environ.get("TOR_CONTROL_PASSWORD", None)  # plain password (optional)
TOR_CONTROL_USE_COOKIE = os.environ.get("TOR_CONTROL_USE_COOKIE", "1") == "1"

# Upstream service used to determine IP (change if you prefer)
IP_CHECK_URL = os.environ.get("IP_CHECK_URL", "https://httpbin.org/ip")

# Flask app
app = Flask(__name__, static_folder=SITE_DIR, static_url_path="")

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tor-server")


def set_security_headers(response):
    """
    Basic security headers. Adjust CSP as needed for your UI.
    """
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    # Minimal Content Security Policy - allow scripts/styles from self only.
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    return response


@app.after_request
def add_security_headers(response):
    return set_security_headers(response)


@app.route("/", methods=["GET"])
def index():
    """Serve the UI index.html from the site directory."""
    index_path = os.path.join(SITE_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(SITE_DIR, "index.html")
    return "Index file not found", 404


@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    """Serve any other static file from site/ (css, js, images)."""
    target = os.path.join(SITE_DIR, path)
    if os.path.exists(target):
        return send_from_directory(SITE_DIR, path)
    return "Not found", 404


def fetch_ip_via_requests(url=IP_CHECK_URL, proxies=None, timeout=6):
    """
    Return IP string fetched from a simple JSON service (httpbin.org/ip or ipify).
    Returns None on failure.
    """
    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # httpbin returns {"origin": "1.2.3.4"} ; ipify returns {"ip":"1.2.3.4"}
        return data.get("origin") or data.get("ip") or None
    except RequestException as exc:
        logger.debug("IP fetch failed: %s", exc)
        return None
    except ValueError:
        logger.debug("IP fetch: unexpected response body")
        return None


@app.route("/api/ip", methods=["GET"])
def api_ip():
    """
    Return both the default outward-facing IP and the IP when routing through Tor.
    Example response:
      { "default": "1.2.3.4", "tor": "5.6.7.8" }
    """
    default_ip = fetch_ip_via_requests()
    tor_ip = fetch_ip_via_requests(proxies=TOR_SOCKS_PROXY)
    return jsonify({"default": default_ip, "tor": tor_ip}), 200


@app.route("/api/newnym", methods=["POST"])
def api_newnym():
    """
    Request a NEWNYM (new identity) from the local Tor instance via ControlPort.
    Requires Tor control auth (password or cookie). If stem isn't installed, return an error.
    """
    if not HAVE_STEM:
        return jsonify({"status": "error", "message": "stem library not installed on server"}), 500

    # Bind to the configured control address/port
    try:
        controller = Controller.from_port(address=TOR_CONTROL_HOST, port=TOR_CONTROL_PORT, timeout=5)
    except Exception as exc:
        logger.exception("Failed to connect to Tor control port")
        return jsonify({"status": "error", "message": f"Failed to connect to Tor control port: {exc}"}), 500

    try:
        # Authenticate: prefer password if set, else cookie if enabled, else try unauthenticated (rare)
        if TOR_CONTROL_PASSWORD:
            controller.authenticate(password=TOR_CONTROL_PASSWORD)
        elif TOR_CONTROL_USE_COOKIE:
            controller.authenticate()  # will attempt cookie authentication
        else:
            controller.authenticate()  # fallback, may raise
    except Exception as exc:
        logger.exception("Tor control authentication failed")
        return jsonify({"status": "error", "message": "Tor control auth failed: " + str(exc)}), 403

    try:
        controller.signal(Signal.NEWNYM)
        controller.close()
        return jsonify({"status": "ok", "message": "SIGNAL NEWNYM sent"}), 200
    except Exception as exc:
        logger.exception("Failed to signal NEWNYM")
        return jsonify({"status": "error", "message": "Failed to send NEWNYM: " + str(exc)}), 500


if __name__ == "__main__":
    # Development server - binds to localhost only by default
    logger.info("Starting Flask server on %s:%s (serving site from %s)", HOST, PORT, SITE_DIR)
    app.run(host=HOST, port=PORT, debug=False)
