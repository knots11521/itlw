#!/usr/bin/env bash
# Install the Pygame-only runtime on Raspberry Pi OS Bookworm (64-bit) or later.
set -euo pipefail

project_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

sudo apt update
# Panda3D is no longer used, so OpenGL/EGL runtime packages are unnecessary.
sudo apt install -y python3-full python3-venv

python3 -m venv "$project_dir/.venv"
"$project_dir/.venv/bin/python" -m pip install --upgrade pip
"$project_dir/.venv/bin/python" -m pip install -r "$project_dir/requirements.txt"

printf '\nInstallation complete. Start the application with:\n'
printf '  bash scripts/run_raspberry_pi.sh\n'
