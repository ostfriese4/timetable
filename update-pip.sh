#! /bin/bash

wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/refs/heads/master/pip/flatpak-pip-generator.py
python flatpak-pip-generator.py --requirements-file='pypi.txt' --output pypi.json
rm flatpak-pip-generator.py