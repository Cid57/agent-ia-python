#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Ajouter le répertoire courant au chemin d'accès pour importer les modules
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Cette variable est utilisée par PythonAnywhere
application = app

if __name__ == "__main__":
    app.run() 