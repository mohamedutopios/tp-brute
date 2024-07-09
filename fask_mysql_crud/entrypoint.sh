#!/bin/bash

# Attendre que la base de données soit disponible
while ! nc -z db 3306; do
  echo "Waiting for the database..."
  sleep 1
done

# Initialiser et migrer la base de données
flask db init || true
flask db migrate -m "Initial migration." || true
flask db upgrade || true

exec "$@"
