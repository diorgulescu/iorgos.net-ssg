#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RESTORE SCRIPT // Revert to original Tactical HUD design from _backup_tactical_hud
Usage: python3 restore_backup.py

Copyright (C) 2026 Dragoș Iorgulescu <dragos@iorgos.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "_backup_tactical_hud"

if not BACKUP_DIR.exists():
    print("[ERR] Backup directory _backup_tactical_hud not found.")
    exit(1)

items = [
    "index.html", "now.html", "publish.py", "build_tactical_site.py", 
    "README.md", "README.en.md", "css", "js", "blog", "howto", 
    "programe", "sounds", "kettlebell"
]

for item in items:
    src = BACKUP_DIR / item
    dst = BASE_DIR / item
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    elif src.is_file():
        shutil.copy2(src, dst)

print("[SYS // RESTORE] Restored original Tactical HUD design from _backup_tactical_hud successfully.")
