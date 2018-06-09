import archiveis
import praw
import csv


def bot_login(identifiers):
    login = praw.Reddit(**identifiers)
    return login


with open("identifiers.csv") as id_csv:
    reader = csv.reader(id_csv)
    imported_id = {row[0]: row[1] for row in reader}

reddit = bot_login(imported_id)
subreddit = reddit.subreddit("badmathematics")
test = reddit.subreddit("testingground4bots")

for submission in test.stream.submissions(skip_existing=True):
    if submission:
        archive_url = archiveis.capture(submission.url)
        comment_text = f"[Here's]({archive_url}) an archived version of this thread.  \n"\
                       f"[^^Source](https://github.com/kitegi/discount-gv)"
        submission.reply()
        print("Reply sent successfully")
