#!/bin/bash

set -e

# Set required Vault env vars
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=vault-plaintext-root-token

# Load license from .env if not already in env
if [ -z "$LIQUIBASE_PRO_LICENSE" ]; then
  echo "No LIQUIBASE_PRO_LICENSE found — trying to load from .env"
  if [ -f .env ]; then
    export $(grep LIQUIBASE_PRO_LICENSE .env | xargs)
    echo "✅ Loaded license from .env"
  else
    echo "❌ ERROR: No license available! Exiting."
    exit 1
  fi
fi

echo "✅ License ready for use."

# Kill any running containers
echo "*** Cleaning up old containers..."
docker rm -f postgres-dev postgres-qa postgres-prod vault-server >/dev/null 2>&1 || true

echo "*** Pulling images..."
docker pull postgres
docker pull hashicorp/vault:1.14.4

echo "*** Starting PostgreSQL containers..."
docker run --name postgres-dev -p 5433:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-qa -p 5434:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-prod -p 5435:5432 -e POSTGRES_PASSWORD=secret -d postgres

echo "*** Starting Vault in host background (dev mode)..."
pkill vault || true
vault server -dev -dev-root-token-id=vault-plaintext-root-token > /tmp/vault.log 2>&1 &
sleep 5

echo "*** Waiting for Vault to become ready..."
until curl -s $VAULT_ADDR/v1/sys/health | grep '"initialized":true' >/dev/null; do
  sleep 2
done

echo "*** Writing secrets to Vault from host..."
vault kv put secret/liquibase/credentials username=postgres password=secret
vault kv put secret/liquibase/license pro_key="$LIQUIBASE_PRO_LICENSE"

echo "*** Copying SQL files into containers..."
docker cp SQL/Tables_DEV.sql postgres-dev:/tmp/Tables_DEV.sql || echo "⚠️ Missing Tables_DEV.sql"
docker cp SQL/Tables_QA.sql postgres-qa:/tmp/Tables_QA.sql || echo "⚠️ Missing Tables_QA.sql"

echo "*** Running schema for postgres-dev..."
docker exec -i postgres-dev bash -c "psql -U postgres -a -f /tmp/Tables_DEV.sql" || echo "⚠️ Failed to load DEV schema"

echo "*** Running schema for postgres-qa..."
docker exec -i postgres-qa bash -c "psql -U postgres -a -f /tmp/Tables_QA.sql" || echo "⚠️ Failed to load QA schema"

echo "✅ Demo environment setup complete: PostgreSQL + Vault is ready."
