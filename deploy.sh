#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════
#  PhaseForge — Update Script (pull from Git repo)
#  Target: Ubuntu 22.04 / 24.04  |  IP: 35.207.153.112
#  Domain: phaseforge.dpdns.org
# ═══════════════════════════════════════════════════════
set -e

APP_DIR="/var/www/phaseforge"
DOMAIN="phaseforge.dpdns.org"
SERVICE="phaseforge"
BRANCH="main"                     # Change to your default branch (master/main)

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   PhaseForge Update Script (git pull)    ║"
echo "╚══════════════════════════════════════════╝"
echo ""


# ── 1. Pull latest changes ──────────────────────────
echo "▶ Pulling latest code from $BRANCH branch..."
cd "$APP_DIR"
sudo -u www-data git fetch origin
sudo -u www-data git checkout "$BRANCH"
sudo -u www-data git pull origin "$BRANCH"

# ── 2. Update Python dependencies (if requirements.txt changed) ──
echo "▶ Updating Python dependencies..."
sudo -u www-data "$APP_DIR/venv/bin/pip" install --upgrade pip -q
sudo -u www-data "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q

# ── 4. Restart the application service ───────────────
echo "▶ Restarting $SERVICE service..."
sudo systemctl daemon-reload
sudo systemctl restart "$SERVICE"
sudo systemctl status "$SERVICE" --no-pager

# ── 5. Reload Nginx (only if static files or config changed) ──
echo "▶ Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✓  Update complete!                    ║"
echo "║   Open: https://$DOMAIN         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status  $SERVICE"
echo "  sudo systemctl restart $SERVICE"
echo "  sudo journalctl -u $SERVICE -f   # live logs"
echo "  sudo nginx -t && sudo systemctl reload nginx"