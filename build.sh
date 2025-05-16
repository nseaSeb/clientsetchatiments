#!/bin/bash

# Nettoyage préalable (optionnel)
rm -rf build/ dist/ *.spec
# Extraction des métadonnées depuis version.py
APP_NAME=$(python3 -c "from version import APP_NAME; print(APP_NAME)")
VERSION=$(python3 -c "from version import VERSION; print(VERSION)")
AUTHOR=$(python3 -c "from version import AUTHOR; print(AUTHOR)")
DESCRIPTION=$(python3 -c "from version import DESCRIPTION; print(DESCRIPTION)")

# Compilation avec PyInstaller
# Compilation avec PyInstaller
pyinstaller --windowed \
  --icon=resources/app.icns \
  --name="$APP_NAME" \
  --icon="resources/app.icns" \
  --target-arch universal2 \
  app.py