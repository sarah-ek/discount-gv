import archiveis
import praw
import csv
from time import sleep


def bot_login(identifiers):
    login = praw.Reddit(**identifiers)
    return login


with open("identifiers.csv") as id_csv:
    reader = csv.reader(id_csv)
    imported_id = {row[0]: row[1] for row in reader}

reddit = bot_login(imported_id)
subreddit = reddit.subreddit("badmathematics")
submission_stream = subreddit.stream.submissions(skip_existing=True, pause_after=0)

while True:
    submission = next(submission_stream)
    if submission:
        if len(submission.selftext) == 0:
            url = submission.url
            if url.startswith("https://www.reddit.com"):
                url = url[0:8] + 'old' + url[11:]
            archive_url = archiveis.capture(url)
            comment_text = f"[Here's]({archive_url}) an archived version of this thread.  \n" \
                           f"[^^Source](https://github.com/kitegi/discount-gv)"
            submission.reply(comment_text)
            print("Reply sent successfully")
    else:
        sleep(60)
