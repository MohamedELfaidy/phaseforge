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

# Check if app directory exists and is a git repo
if [ ! -d "$APP_DIR/.git" ]; then
    echo "❌ $APP_DIR is not a Git repository."
    echo "   Please clone your repo first:"
    echo "   sudo -u www-data git clone <your-repo-url> $APP_DIR"
    exit 1
fi

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

# ── 3. Run any Django migrations or build steps (if needed) ──
# Example for Django:
# echo "▶ Running migrations..."
# sudo -u www-data "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" migrate --noinput
#
# Example for static files:
# sudo -u www-data "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

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