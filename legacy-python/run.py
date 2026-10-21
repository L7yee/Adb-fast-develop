"""
ADB Debug Dashboard - Entry point script.

Run this script to start the application:
    python run.py
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adb_dashboard.main import main

if __name__ == "__main__":
    main()
