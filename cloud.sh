#!/usr/bin/env bash

echo """
 _      ____  ____  _     
/ \__/|/  _ \/  _ \/ \  /|
| |\/||| / \|| / \|| |\ ||
| |  ||| \_/|| \_/|| | \||
\_/  \|\____/\____/\_/  \|
                          
Copyright (C) 2020-2023 by MoonTg-project@Github, < https://github.com/The-MoonTg-project >.
This file is part of < https://github.com/The-MoonTg-project/Moon-Userbot > project,
and is released under the "GNU v3.0 License Agreement".
Please see < https://github.com/The-MoonTg-project/Moon-Userbot/blob/main/LICENSE >
All rights reserved.
"""

gunicorn app:app --daemon && python main.py