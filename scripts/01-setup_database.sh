#!/bin/bash


echo "Running database migrations..."
poetry run alembic upgrade head
echo "Migrations completed successfully!"

echo "Database setup complete!"
