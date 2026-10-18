git commit -m "Initial commit: Add install-tor.sh"
install-tor.sh
#!/usr/bin/env bash
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing Tor..."
sudo apt install -y tor

echo "Enabling and starting Tor service..."
sudo systemctl enable --now tor

echo "Tor installation finished."
echo "Checking Tor service status:"
sudo systemctl --no-pager status tor
