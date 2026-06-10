#!/bin/sh
set -e
python scripts/wait_for_db.py
flask --app run.py init-db
exec gunicorn -b 0.0.0.0:5000 run:app
