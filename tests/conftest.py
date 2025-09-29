"""Pytest configuration for the project."""
from __future__ import annotations

import os
import sys

# Ensure the application package is on sys.path when tests are executed from anywhere.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
