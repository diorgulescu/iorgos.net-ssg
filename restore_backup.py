#!/usr/bin/env python3
"""
RESTORE SCRIPT // Revert to original Tactical HUD design from _backup_tactical_hud
Usage: python3 restore_backup.py
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
