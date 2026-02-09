#!/usr/bin/env bash

BIND_ADDR="0.0.0.0:${PORT:-8000}"

cat <<'EOF'
 _      ____  ____  _     
/ \__/|/  _ \/  _ \/ \  /|
| |\/||| / \|| / \|| |\ ||
| |  ||| \_/|| \_/|| | \||
\_/  \|\____/\____/\_/  \|
                          
Copyright (C) 2020-2025 by MoonTg-project@Github, < https://github.com/The-MoonTg-project >.
This file is part of < https://github.com/The-MoonTg-project/Moon-Userbot > project,
and is released under the "GNU v3.0 License Agreement".
Please see < https://github.com/The-MoonTg-project/Moon-Userbot/blob/main/LICENSE >
All rights reserved.
EOF

echo "Starting gunicorn server on $BIND_ADDR..."
gunicorn app:app --daemon --bind "$BIND_ADDR" && python main.py
