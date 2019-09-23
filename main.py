import csv
from pathlib import Path
from time import time

import godel

with open("identifiers.csv") as id_csv:
    reader = csv.reader(id_csv)
    imported_id = {row[0]: row[1] for row in reader}

Path("logs").mkdir( exist_ok=True)
last_update = Path("logs/last-update")
if not last_update.exists() or (time() - last_update.stat().st_mtime > 1800):
    reddit = godel.bot_login(imported_id)
    subreddit = reddit.subreddit("badmathematics")
    godel.reply_to_missed(reddit, subreddit, time_limit=7200)
    last_update.touch()
