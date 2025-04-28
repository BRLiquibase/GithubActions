#!/bin/bash

set -e  # Exit immediately if a command fails

# Emoji helpers
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function success() {
  echo -e "${GREEN}✅ $1${NC}"
}

echo "*** Cleaning up old containers..."
docker rm -f postgres-dev postgres-qa postgres-prod vault-server || true
success "Old containers cleaned up."

echo "*** Pulling images..."
docker pull postgres
docker pull hashicorp/vault:1.14.4
success "Docker images pulled."

echo "*** Starting PostgreSQL containers..."
docker run --name postgres-dev -p 5433:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-qa -p 5434:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-prod -p 5435:5432 -e POSTGRES_PASSWORD=secret -d postgres
success "Postgres containers started."

echo "*** Starting Vault dev server..."
docker run --name vault-server -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=vault-plaintext-root-token \
  -e VAULT_ADDR=http://0.0.0.0:8200 \
  -d hashicorp/vault:1.14.4 server -dev -dev-root-token-id=vault-plaintext-root-token
success "Vault server started."

echo "*** Waiting for services to be ready..."
sleep 10
success "Services are ready."

echo "*** Writing secrets to Vault..."
docker exec -i vault-server sh <<EOF
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=vault-plaintext-root-token

vault kv put secret/liquibase/credentials username=postgres password=secret

vault kv put secret/liquibase/license pro_key="$LIQUIBASE_LICENSE_KEY"
EOF
success "Secrets written to Vault."

echo "*** Copying SQL files into containers..."
docker cp SQL/Tables_DEV.sql postgres-dev:/tmp/Tables_DEV.sql
docker cp SQL/Tables_QA.sql postgres-qa:/tmp/Tables_QA.sql
success "SQL files copied."

echo "*** Running schema for postgres-dev..."
docker exec -i postgres-dev bash -c "psql -U postgres -a -f /tmp/Tables_DEV.sql"
success "Schema loaded for postgres-dev."

echo "*** Running schema for postgres-qa..."
docker exec -i postgres-qa bash -c "psql -U postgres -a -f /tmp/Tables_QA.sql"
success "Schema loaded for postgres-qa."

echo "*** Demo environment setup complete: PostgreSQL + Vault is ready."
success "Environment fully setup."

########################################
# NEW: Start GitHub Actions Runner
########################################

echo "*** Starting GitHub Actions runner in background..."

cd actions-runner  

# Start runner quietly in background
nohup ./run.sh > /dev/null 2>&1 &

success "GitHub Actions runner started in background."
