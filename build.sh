#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create instance directory if it doesn't exist
mkdir -p instance

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run database migrations if migrations directory exists
if [ -d "migrations" ]; then
  flask db upgrade
fi
