#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

TOR_SOCKS = "127.0.0.1:9050"  # default Tor socks port

def start_system_tor():
    """Try to start system tor if available; return subprocess or None.
       On Windows you may want to point to a bundled tor.exe instead."""
    tor_cmd = shutil.which("tor")
    if not tor_cmd:
        return None
    try:
        # start tor in background (stdout/stderr redirected)
        p = subprocess.Popen([tor_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p
    except Exception:
        return None

def ensure_qtproxy(flags=None):
    """Set Chromium flags for Qt WebEngine so it uses Tor's SOCKS proxy."""
    # Use socks5 with host DNS resolution remote (socks5h semantics)
    # Setting environment variable before QtWebEngine is imported
    proxy_flag = '--proxy-server="socks5://%s"' % TOR_SOCKS
    chromium_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
    if chromium_flags:
        chromium_flags += " " + proxy_flag
    else:
        chromium_flags = proxy_flag
    if flags:
        chromium_flags += " " + flags
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = chromium_flags

class TorBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Tor Browser")
        self.resize(1200, 800)
        self.web = QWebEngineView(self)
        self.setCentralWidget(self.web)

        nav = QToolBar("Navigation")
        self.addToolBar(nav)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.load_url)

        back = QAction("Back", self)
        back.triggered.connect(self.web.back)
        nav.addAction(back)

        forward = QAction("Forward", self)
        forward.triggered.connect(self.web.forward)
        nav.addAction(forward)

        reload = QAction("Reload", self)
        reload.triggered.connect(self.web.reload)
        nav.addAction(reload)

        nav.addWidget(self.urlbar)

        # update URL bar on change
        self.web.urlChanged.connect(self.on_url_changed)

        # initial page
        self.web.setUrl(QUrl("https://check.torproject.org/"))

    def load_url(self):
        url = self.urlbar.text().strip()
        if not url:
            return
        if "://" not in url:
            url = "http://" + url
        self.web.load(QUrl(url))

    def on_url_changed(self, qurl):
        self.urlbar.setText(qurl.toString())

def main():
    # set up proxy flags before importing/initializing QtWebEngine internals
    ensure_qtproxy()
    # Optionally start Tor here if tor binary is available and you want an embedded start.
    tor_proc = start_system_tor()
    app = QApplication(sys.argv)
    w = TorBrowser()
    w.show()
    try:
        rc = app.exec_()
    finally:
        if tor_proc:
            tor_proc.terminate()
    sys.exit(rc)

if __name__ == "__main__":
    main()
