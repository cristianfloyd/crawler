#!/bin/bash
echo "Starting Jupyter Lab and Marimo..."
export LANG=es_ES.UTF-8
export LC_ALL=es_ES.UTF-8

# Start Jupyter Lab in foreground
echo "Starting Jupyter Lab on port 8888..."
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password="" --LabApp.language_pack='es_ES' &

# Start Marimo in background
echo "Starting Marimo on port 8080..."
marimo edit --host 0.0.0.0 --port 8080 --headless