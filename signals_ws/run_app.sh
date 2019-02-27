#!/bin/sh
gunicorn --name 'Turbines Signals App'  --bind 0.0.0.0:80 app:app -k gevent --worker-connections 10000 
