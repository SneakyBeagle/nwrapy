#!/bin/bash

printf "[+] Pulling from git repository\n"
git pull

printf "[+] Installing latest version\n"
./install.sh
