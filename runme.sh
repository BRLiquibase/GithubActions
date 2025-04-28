#!/bin/bash

echo "*** Cleaning up old containers..."
docker rm -f postgres-dev postgres-qa postgres-prod vault-server

echo "*** Pulling images..."
docker pull postgres
docker pull hashicorp/vault:1.14.4

echo "*** Starting PostgreSQL containers..."
docker run --name postgres-dev -p 5433:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-qa -p 5434:5432 -e POSTGRES_PASSWORD=secret -d postgres
docker run --name postgres-prod -p 5435:5432 -e POSTGRES_PASSWORD=secret -d postgres

echo "*** Starting Vault dev server..."
docker run --name vault-server -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=vault-plaintext-root-token \
  -e VAULT_ADDR=http://0.0.0.0:8200 \
  -d hashicorp/vault:1.14.4 server -dev -dev-root-token-id=vault-plaintext-root-token

echo "*** Waiting for services to be ready..."
sleep 10

echo "*** Writing secrets to Vault..."

docker exec -i vault-server sh <<EOF
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=vault-plaintext-root-token

vault kv put secret/liquibase/credentials username=postgres password=secret

vault kv put secret/liquibase/license pro_key="ABwwGgQUmZ98FMuIT3R0lsu3oQWCkpGy0kkCAgQA3O4GsLK9z+UfiIX/4nj36rHtogQ/tfFJ+lqX1zL2VqNx35y6AR8/imw52vNQXCWop7oUPt1ILALR0qguohnPMJJfKNhIq+ydZaMj29/cgRrKo/N65eZTr6p7s3ZhC0cdQqLdTPRnjucs0oYxfJ62pUN+ItB2CtLo8tn/51sKfgPf+XO55ZkCLHiCRAud4Zw3zQvzqN0h3fwu9HOGcGLxMyWJvxo/3H6L7BTPtVfhU+emWP9+0n2mIMDAAPeDuL45J27cB8lOJwwAjSWjOOxDwzxy6UbWbeyfCMnylFGWTbwd9Lb+S01IaGU8eTTIZA5vDRdGN0CSUBH4KabvemfuabDWw/aCaoWEQd+ZH5RgstfPi1+b0GxalQHJh1ced1J6ydEYpXiusYe9tOA8tuolOc3qkjtrYGziOWSf2SdtdOYiLgI96BsqB45HB4cN16asY01sFjBo/giCW6k7LuQlwLfbb1tqFiKXf1QhpJaP0vfL6Oyjp0+HhNg0oX0Zobm6oMv/DnWXVs8eWBcaNEXNBZAtHKMAXSP4h9JgGDzQ7eQbgrEdIW833bR8b1aEmsg2MtTGwLI1JZN9xd3CGrW5+0U2791A/3ruAnA94rkneB/UCLUUaCxxXimIebCB/dtzpQzC8IDYKmZyVCCsK2qC5hKRKWYKzO8lof1bIl5QWGdKP9doiHsBFw=="
EOF

echo "*** Copying SQL files into containers..."
docker cp SQL/Tables_DEV.sql postgres-dev:/tmp/Tables_DEV.sql
docker cp SQL/Tables_QA.sql postgres-qa:/tmp/Tables_QA.sql

echo "*** Running schema for postgres-dev..."
docker exec -i postgres-dev bash -c "psql -U postgres -a -f /tmp/Tables_DEV.sql"

echo "*** Running schema for postgres-qa..."
docker exec -i postgres-qa bash -c "psql -U postgres -a -f /tmp/Tables_QA.sql"

echo "*** Demo environment setup complete: PostgreSQL + Vault is ready."

