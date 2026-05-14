#!/usr/bin/env bash
set -e

APP_DIR="/var/www/phaseforge"
DOMAIN="phaseforge.dpdns.org"
REPO="https://github.com/MohamedELfaidy/phaseforge.git"
SERVICE="phaseforge"

echo ""
echo "=================================="
echo "PhaseForge deployment started"
echo "=================================="

echo "Installing packages..."
sudo apt update

sudo apt install -y \
python3 \
python3-pip \
python3-venv \
git \
nginx \
certbot \
python3-certbot-nginx

sudo mkdir -p /var/log/phaseforge

if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repository..."
    sudo git clone "$REPO" "$APP_DIR"
else
    echo "Repository exists. Pulling latest changes..."
    cd "$APP_DIR"
    sudo git pull
fi

sudo chown -R www-data:www-data "$APP_DIR"
sudo chown -R www-data:www-data /var/log/phaseforge

echo "Creating virtual environment..."

if [ ! -d "$APP_DIR/venv" ]; then
    sudo -u www-data python3 -m venv "$APP_DIR/venv"
fi

sudo -u www-data "$APP_DIR/venv/bin/pip" install --upgrade pip

sudo -u www-data \
"$APP_DIR/venv/bin/pip" install -r \
"$APP_DIR/requirements.txt"

echo "Installing nginx config..."

sudo cp "$APP_DIR/deploy/nginx.conf" \
/etc/nginx/sites-available/phaseforge

sudo ln -sf \
/etc/nginx/sites-available/phaseforge \
/etc/nginx/sites-enabled/phaseforge

sudo nginx -t
sudo systemctl reload nginx

echo "Installing service..."

sudo cp "$APP_DIR/deploy/phaseforge.service" \
/etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable phaseforge

sudo systemctl restart phaseforge

echo "Obtaining SSL..."

if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then

sudo certbot --nginx \
-d "$DOMAIN" \
-d "www.$DOMAIN" \
--non-interactive \
--agree-tos \
-m "admin@$DOMAIN"

sudo systemctl reload nginx

else
    echo "SSL already exists."
fi

echo ""
echo "Deployment complete."
echo ""

echo "Useful commands:"
echo "sudo systemctl status phaseforge"
echo "sudo journalctl -u phaseforge -f"
echo "sudo systemctl restart phaseforge"