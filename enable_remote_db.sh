#!/bin/bash
set -e

# Detect Postgres version (assuming only one is installed/active or taking the latest)
PG_VERSION=$(ls /etc/postgresql | sort -V | tail -n1)

if [ -z "$PG_VERSION" ]; then
  echo "Error: PostgreSQL configuration directory not found in /etc/postgresql"
  exit 1
fi

CONF_DIR="/etc/postgresql/$PG_VERSION/main"
echo "Found PostgreSQL version $PG_VERSION. Config directory: $CONF_DIR"

echo "Backing up configurations..."
sudo cp "$CONF_DIR/postgresql.conf" "$CONF_DIR/postgresql.conf.bak_$(date +%s)"
sudo cp "$CONF_DIR/pg_hba.conf" "$CONF_DIR/pg_hba.conf.bak_$(date +%s)"

echo "Enabling listen_addresses = '*' in postgresql.conf..."
# Uncomment if commented
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$CONF_DIR/postgresql.conf"
# Replace if set to localhost (even if uncommented previously or by above)
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$CONF_DIR/postgresql.conf"

echo "Allowing remote connections in pg_hba.conf..."
# Add entry if not exists
if ! grep -q "0.0.0.0/0" "$CONF_DIR/pg_hba.conf"; then
    echo "host    all             all             0.0.0.0/0               scram-sha-256" | sudo tee -a "$CONF_DIR/pg_hba.conf"
    echo "Added allow rule for 0.0.0.0/0"
else
    echo "Rule for 0.0.0.0/0 already exists."
fi

echo "Restarting PostgreSQL service..."
sudo service postgresql restart

echo "Verification:"
sudo ss -nltp | grep 5432

echo "
=====================================================
Database is now configured for remote access.
Connect using:
  Host: $(hostname -I | awk '{print $1}')
  Port: 5432
  User: postgres
  DB:   poline_db
=====================================================
"
