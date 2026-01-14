#!/usr/bin/env bash

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

echo "Starting web server..."
socat TCP-LISTEN:${PORT:-8000},reuseaddr,fork,crlf SYSTEM:'echo "HTTP/1.1 200 OK"; echo "Content-Length: 12"; echo; echo "This is Moon"' &

python main.py
