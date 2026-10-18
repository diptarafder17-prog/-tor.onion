# Tor Installation Project

A simple automation script to install and configure Tor on Debian/Ubuntu Linux.

## How to use:
```bash
git clone [https://github.com/diptarafder17-prog/-tor.onion.git](https://github.com/diptarafder17-prog/-tor.onion.git)
cd -tor.onion
chmod +x install-tor.sh
./install-tor.sh

#### 2. If you want to view your code repository (instead of the hosted webpage):
Visit the repository link directly:
> **`[https://github.com/diptarafder17-prog/-tor.onion](https://github.com/diptarafder17-prog/-tor.onion)`**[span_2](start_span)[span_2](end_span)
# Tor Deep Web Browser Setup

This project provides a lightweight Python browser that routes traffic through a local Tor SOCKS5 proxy.

Important:
- This is not a replacement for the official Tor Browser.
- For real anonymity and security, use the official Tor Browser provided by Tor Project.
- This tool is intended for local testing and learning.

## Requirements
- Linux (tested on Debian/Ubuntu)
- Python 3
- Tor installed and running locally
- PyQt5 and PyQtWebEngine

## Install Tor
```bash
sudo apt update
sudo apt install -y tor
sudo systemctl enable --now tor
