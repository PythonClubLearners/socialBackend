import json
import os
from pathlib import Path

__all__ = ["default_database"]

BASE_DIR = Path(__file__).resolve().parent

if not os.path.exists(os.path.join(BASE_DIR, 'config.json')):
    with open(os.path.join(BASE_DIR, 'config.json'), 'w', encoding='utf-8') as config_file:
        json.dump({
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }, config_file, ensure_ascii=False, indent=4)


with open(os.path.join(BASE_DIR, 'config.json'), 'r', encoding='utf-8') as config_file:

    default_database = json.load(config_file)
