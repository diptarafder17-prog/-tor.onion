
#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y tor
sudo systemctl enable --now tor

echo "Tor installation finished."
systemctl --no-pager status tor
