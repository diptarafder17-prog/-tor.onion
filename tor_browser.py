#!/usr/bin/env python3
"""
Minimal Tor browser using QtWebEngine configured to use Tor SOCKS5 proxy.
This is a simple testing/browser prototype, not a replacement for the official Tor Browser.
"""

import os
import sys
import subprocess

# Force the Qt WebEngine browser to use Tor's SOCKS5 proxy.
# This works only if Tor is running locally on 127.0.0.1:9050.
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    '--proxy-server="socks5://127.0.0.1:9050"'
)

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QLineEdit, QToolBar, QMainWindow, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView


class TorBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tor Browser")
        self.resize(1200, 800)

        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        nav = QToolBar("Navigation")
        self.addToolBar(nav)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.webview.back)
        nav.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.webview.forward)
        nav.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.webview.reload)
        nav.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(lambda: self.load_url("https://check.torproject.org/"))
        nav.addAction(home_btn)

        self.urlbar = QLineEdit(self)
        self.urlbar.returnPressed.connect(self.on_enter_url)
        nav.addWidget(self.urlbar)

        self.webview.urlChanged.connect(self.update_urlbar)

        # Load default page
        self.load_url("https://check.torproject.org/")

    def load_url(self, url):
        if not url:
            return
        if not (url.startswith("http://") or url.startswith("https://") or url.endswith(".onion")):
            url = "http://" + url
        self.webview.load(QUrl(url))

    def on_enter_url(self):
        url = self.urlbar.text().strip()
        if not url:
            return
        if url.endswith(".onion") and not url.startswith("http"):
            url = "http://" + url
        self.load_url(url)

    def update_urlbar(self, qurl):
        self.urlbar.setText(qurl.toString())


def ensure_tor_running():
    try:
        result = subprocess.run(
            ["tor", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False
        )
        if result.returncode != 0:
            print("Tor is not installed or not in PATH.")
            print("Install Tor first, then restart this browser.")
            return False
    except Exception:
        print("Tor command not found. Install Tor first.")
        return False
    return True


def main():
    if not ensure_tor_running():
        sys.exit(1)

    try:
        app = QApplication(sys.argv)
        browser = TorBrowser()
        browser.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Failed to start browser: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
