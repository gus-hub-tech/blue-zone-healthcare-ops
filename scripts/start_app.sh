#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install dependencies if not already installed
pip install -q -r app/requirements.txt

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
