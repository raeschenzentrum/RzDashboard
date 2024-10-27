# app/__init__.py
import sys
import os

# Setze den Root-Pfad explizit auf das `app`-Verzeichnis
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)