#!/usr/bin/env python3
"""
Main entry point for RGM Data Generator
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generate_rgm_data import main

if __name__ == "__main__":
    main()