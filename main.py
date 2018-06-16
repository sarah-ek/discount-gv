from prawcore.exceptions import PrawcoreException
import csv
import functions as func
from time import sleep


with open("identifiers.csv") as id_csv:
    reader = csv.reader(id_csv)
    imported_id = {row[0]: row[1] for row in reader}

while True:
    try:
        reddit = func.bot_login(imported_id)
        subreddit = reddit.subreddit("badmathematics")
        submission_stream = subreddit.stream.submissions(skip_existing=True, pause_after=0)
        func.reply_to_missed(reddit, subreddit, number_limit=5, time_limit=1800)
        for submission in submission_stream:
            if submission:
                func.archive_and_reply(submission, sleep_time=60)
        # If submission stream has died, restart the bot after a while
        sleep(60)
        print("Reconnecting...")
    except PrawcoreException as e:
        print(e)
        sleep(300)
        print("Reconnecting...")
