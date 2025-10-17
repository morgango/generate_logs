#!/bin/bash
# Activation script for the log generator virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated!"
echo "You can now run: python3 generate_logs.py [options]"
echo "Or use: python3 generate_logs.py --help for options"
