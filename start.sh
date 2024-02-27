#!/bin/bash

/home/rednamed/.local/bin/poetry run python mm2.py

# Commit comment
ct="$(date +'%Y:%m:%d-%H:%M:%S')"

# Management
git add .
git commit -m $ct
git push 