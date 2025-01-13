#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers using Python3's -m option
python3 -m playwright install