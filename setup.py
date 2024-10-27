# setup.py im Projekt-Root
from setuptools import setup, find_packages

setup(
    name="mein_app_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        # Füge weitere Abhängigkeiten hinzu
    ],
)
