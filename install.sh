#!/bin/bash

target_dir=/usr/bin/
executable=nwrapy
mainfile=nwrapy


# Setup virtual environment and install requirements
printf "[+] Creating and setting up virtual environment\n"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# Remove existing binaries
printf "[+] Removing existing executables and build directories from working dir\n"
if [ -d dist/ ]; then
    rm -rf dist/
fi
if [ -d build/ ]; then
    rm -rf build/
fi

# Create single file executable
printf "[+] Creating executable: "$executable"\n"
pyinstaller $mainfile --onefile

printf "[+] Moving executable to "$target_dir"\n"
sudo cp dist/$executable $target_dir$executable
printf "[+] Executable installed at "$target_dir$executable"\n"

# Cleanup
printf "[+] Cleaning up\n"
deactivate
rm *.spec
rm -rf build/
rm -rf dist/
rm -rf __pycache__/

printf "[+] Done\n"
