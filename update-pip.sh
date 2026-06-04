#! /bin/bash

wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/refs/heads/master/pip/flatpak-pip-generator.py
python flatpak-pip-generator.py --requirements-file='pypi.txt' --output pypi.json --runtime='org.gnome.Sdk//50'
rm flatpak-pip-generator.py

git add pypi.json
git commit -m "updated dependencies"