#!/bin/bash

echo "✅ Cleaning up old containers..."
docker rm -f postgres-dev postgres-qa postgres-prod vault-server 2>/dev/null

echo "✅ Pulling images..."
docker pull postgres
docker pull hashicorp/vault:1.14.4

echo "✅ Starting PostgreSQL containers..."
docker run --name postgres-dev -p 5433:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-qa -p 5434:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-prod -p 5435:5432 -e POSTGRES_PASSWORD=secret -d postgres

echo "✅ Starting Vault dev server..."
docker run --name vault-server -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=vault-plaintext-root-token \
  -e VAULT_ADDR=http://0.0.0.0:8200 \
  -d hashicorp/vault:1.14.4 server -dev -dev-root-token-id=vault-plaintext-root-token

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Reading secrets from .env file..."

# Load the .env file
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ .env file not found. Aborting."
  exit 1
fi

echo "✅ Writing secrets to Vault..."

docker exec vault-server sh -c "
  export VAULT_ADDR=http://localhost:8200
  export VAULT_TOKEN=vault-plaintext-root-token

  vault kv put secret/liquibase/credentials username=postgres password=secret
  vault kv put secret/liquibase/license pro_key=\"$LIQUIBASE_PRO_LICENSE\"
"

echo "✅ Copying SQL files into containers..."
docker cp SQL/Tables_DEV.sql postgres-dev:/tmp/Tables_DEV.sql
docker cp SQL/Tables_QA.sql postgres-qa:/tmp/Tables_QA.sql

echo "✅ Running schema for postgres-dev..."
docker exec -i postgres-dev bash -c "psql -U postgres -a -f /tmp/Tables_DEV.sql"

echo "✅ Running schema for postgres-qa..."
docker exec -i postgres-qa bash -c "psql -U postgres -a -f /tmp/Tables_QA.sql"

echo "🎉 Demo environment setup complete: PostgreSQL + Vault is ready."
