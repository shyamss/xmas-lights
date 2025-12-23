#!/bin/bash
set -e

# --- resolve runtime user ---
APP_USER=$(id -un)
APP_HOME=$(getent passwd "$APP_USER" | cut -d: -f6)

APP_NAME=lights
APP_DIR="$APP_HOME/$APP_NAME"
SERVICE="$APP_NAME"
UPDATE_SERVICE="$APP_NAME-update"

REPO_URL=https://github.com/shyamss/xmas-lights.git

echo "== Installing $APP_NAME for user $APP_USER =="

# --- base packages ---
sudo apt update
sudo apt install -y git python3 python3-pip --no-install-recommends

# --- clone repo ---
if [ ! -d "$APP_DIR" ]; then
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

# --- python deps ---
if [ -f requirements.txt ]; then
  pip3 install --user -r requirements.txt
fi

# --- main lights service ---
sudo tee /etc/systemd/system/$SERVICE.service > /dev/null <<EOF
[Unit]
Description=Lights controller
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# --- update script ---
cat > "$APP_DIR/update.sh" <<EOF
#!/bin/bash
set -e

cd "$APP_DIR"

git fetch origin
LOCAL=\$(git rev-parse @)
REMOTE=\$(git rev-parse @{u})

if [ "\$LOCAL" != "\$REMOTE" ]; then
  git pull --ff-only
  sudo systemctl restart $SERVICE
fi
EOF

chmod +x "$APP_DIR/update.sh"

# --- updater service ---
sudo tee /etc/systemd/system/$UPDATE_SERVICE.service > /dev/null <<EOF
[Unit]
Description=Pull lights updates

[Service]
Type=oneshot
User=$APP_USER
ExecStart=$APP_DIR/update.sh
EOF

# --- updater timer ---
sudo tee /etc/systemd/system/$UPDATE_SERVICE.timer > /dev/null <<EOF
[Unit]
Description=Periodic lights update

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

# --- sudo permission (restart only) ---
sudo tee /etc/sudoers.d/$SERVICE-restart > /dev/null <<EOF
$APP_USER ALL=NOPASSWD: /bin/systemctl restart $SERVICE
EOF

sudo chmod 440 /etc/sudoers.d/$SERVICE-restart

# --- enable everything ---
sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE
sudo systemctl enable --now $UPDATE_SERVICE.timer

echo "== Installation complete =="
echo "User        : $APP_USER"
echo "App dir     : $APP_DIR"
echo "Deploy model: pull-based (systemd timer)"
