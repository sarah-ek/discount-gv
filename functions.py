import praw
import time
import archiveis
import random

with open("quotes.txt", "r") as quotes_file:
    quotes = quotes_file.read().splitlines()


def bot_login(identifiers):
    login = praw.Reddit(**identifiers)
    return login


def witty_quote():
    return random.choice(quotes)


def reply_to_missed(reddit, subreddit, number_limit=None, time_limit=None):
    print("Replying to missed posts...")
    submissions = subreddit.new(limit=number_limit)
    for submission in submissions:
        # If posts are too old, stop checking
        if time_limit and time.time() - submission.created_utc > time_limit:
            break
        submission.comments.replace_more(limit=None)
        for comment in submission.comments:
            # If bot has already replied to this submission,
            # move on to the next one
            if comment.author == reddit.user.me():
                break
        else:
            # If loop is not broken, reply to submission
            archive_and_reply(submission)


def archive_and_reply(submission, sleep_time=60):
    if submission and not submission.is_self:
        url = submission.url
        if url.startswith("https://www.reddit.com"):
            url = url[0:8] + 'old' + url[11:]
        archive_url = archiveis.capture(url)
        comment_text = f"{witty_quote()}\n\n" \
                       f"[Here's]({archive_url}) an archived version of this thread.  \n" \
                       "[^^Source](https://github.com/kitegi/discount-gv) ^^| " \
                       "[^^Submit ^^more ^^quotes]" \
                       "(https://www.reddit.com/message/compose/?to=Discount-GV)"
        submission.reply(comment_text)
        print("Reply sent")
    elif not submission:
        time.sleep(sleep_time)
