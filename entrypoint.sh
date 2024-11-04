#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Check if this is first time setup using an environment variable
if [ "$DJANGO_INITIALIZE_DATA" = "true" ]
then
    echo "First time setup detected. Loading initial data..."
    
    # Check if data directory exists
    if [ -d "dev-data/data" ]; then
        # Delete existing data first (optional, comment out if not needed)
        # python dev-data/data/data_loader.py --delete
        
        # Import fresh data
        # python dev-data/data/data_loader.py --import
        
        # Import appointments
        # python dev-data/data/data_loader.py --importDates
        
        echo "Initial data load completed"
    else
        echo "Warning: dev-data directory not found. Skipping initial data load."
    fi
fi

exec "$@"