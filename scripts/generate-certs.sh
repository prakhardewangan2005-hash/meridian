#!/usr/bin/env bash
# Generate a development CA and mTLS certs for controller, agent, operator.
# NOT for production — use a real PKI (cert-manager, step-ca, Vault) there.
set -euo pipefail

OUT="${1:-./pki}"
mkdir -p "$OUT"
cd "$OUT"

echo "==> CA"
openssl genrsa -out ca-key.pem 4096 2>/dev/null
openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 \
  -subj "/CN=meridian-dev-ca" -out ca.pem

gen() {
  local name="$1" cn="$2"
  echo "==> $name ($cn)"
  openssl genrsa -out "${name}-key.pem" 2048 2>/dev/null
  openssl req -new -key "${name}-key.pem" -subj "/CN=${cn}" -out "${name}.csr"
  openssl x509 -req -in "${name}.csr" -CA ca.pem -CAkey ca-key.pem \
    -CAcreateserial -days 825 -sha256 -out "${name}.pem" 2>/dev/null
  rm -f "${name}.csr"
}

gen controller controller
gen agent agent
gen operator operator

rm -f ca.srl
echo "==> done: certs in $OUT"
