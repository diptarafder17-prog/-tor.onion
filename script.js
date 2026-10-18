#!/usr/bin/env python3
"""
Simple PyQt5 browser that forces Chromium (QtWebEngine) to use Tor SOCKS5 proxy.
NOT a replacement for the official Tor Browser. Use for testing/learning only.
"""

import os
# Must set chromium flags BEFORE importing QtWebEngine / PyQt5 so the flags take effect.
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", '--proxy-server="socks5://127.0.0.1:9050"')

import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QLineEdit, QToolBar, QMainWindow, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView

class TorBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Tor Browser (PyQt5)")
        self.resize(1200, 800)

        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        # Simple toolbar with address bar and navigation
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

        # Load a default page that shows whether your traffic is routed through Tor
        self.load_url("https://check.torproject.org/")

        self.webview.urlChanged.connect(self.update_urlbar)

    def load_url(self, url):
        if not (url.startswith("http://") or url.startswith("https://") or url.endswith(".onion")):
            url = "http://" + url
        self.webview.load(QUrl(url))

    def on_enter_url(self):
        url = self.urlbar.text().strip()
        # allow .onion addresses as entered
        if url.endswith(".onion") and not url.startswith("http"):
            url = "http://" + url
        self.load_url(url)

    def update_urlbar(self, qurl):
        self.urlbar.setText(qurl.toString())

def main():
    app = QApplication(sys.argv)
    w = TorBrowser()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
