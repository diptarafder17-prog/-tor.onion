#!/usr/bin/env bash
set -euo pipefail

# Simple launcher for local development.
# Export environment variables or create a .env file (see .env.example)
# Example:
#   export TOR_SOCKS="127.0.0.1:9050"
#   export TOR_CONTROL_PORT=9051
#   export TOR_CONTROL_PASSWORD="mycontrolpassword"
#   ./run.sh

# Activate venv if you use one (uncomment and edit the path)
# source ../venv/bin/activate

# Ensure dependencies installed
pip install -r requirements.txt

# Run with gunicorn bound to localhost
exec gunicorn --bind 127.0.0.1:5000 app:app
