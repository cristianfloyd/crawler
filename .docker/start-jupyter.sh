#!/bin/bash
echo "Starting Jupyter Lab..."
export LANG=es_ES.UTF-8
export LC_ALL=es_ES.UTF-8
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password="" --LabApp.language_pack='es_ES'