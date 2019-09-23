from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from random import randint

import praw
from archiveis import capture
from lxml import etree
from markdown import markdown
from praw.models import Submission

with open("quotes.txt", "r") as quotes_file:
    lines = quotes_file.read().splitlines()
    QUOTES = list(map(lambda quote: quote.replace("\\n", "\n"), lines[::2]))
    REFERENCES = lines[1::2]


def bot_login(identifiers):
    login = praw.Reddit(**identifiers)
    return login


def witty_quote():
    i = randint(0, len(QUOTES) - 1)
    return QUOTES[i], REFERENCES[i]


def signature(source_url):
    return (
        f"\n\n{('[^^Quote](' + source_url +') ^^| ') if source_url != 'NONE' else ''}"
        "[^^Source](https://github.com/kitegi/discount-gv) ^^| "
        "[^^Send ^^a ^^message]"
        "(https://www.reddit.com/message/compose/?to=Discount-GV)"
    )


def reply_to_missed(reddit, subreddit, number_limit=None, time_limit=None):
    count = 0
    submissions = subreddit.new(limit=number_limit)

    now = datetime.utcnow()
    log_file = open("logs/" + now.strftime("%Y-%m-%d.txt"), "a")

    for submission in submissions:
        # Stop checking if posts are too old
        if time_limit and now.timestamp() - submission.created_utc > time_limit:
            break
        submission.comments.replace_more(limit=None)

        already_repled = False
        for comment in submission.comments:
            # Skip submission if we've has already replied
            if comment.author == reddit.user.me():
                already_repled = True
                break
        if not already_repled:
            archive_and_reply(submission, log_file)
            count += 1
    if count == 0:
        print("No submissions found.", file=log_file)
    else:
        print(
            f"{count} submission{{}} found.".format("s" if count > 1 else ""),
            file=log_file,
        )
    log_file.close()


def archive_and_reply(post: Submission, log_file: TextIOWrapper) -> None:
    print(post.title, file=log_file)
    quote, source_url = witty_quote()
    comment_text = f"{quote}\n\n"
    multiple_links = False

    if post.is_self:
        text = post.selftext
        document = etree.fromstring("<items>" + markdown(text) + "</items>")
        links = document.xpath("//a")
        if not links:
            return
        if len(links) > 1:
            multiple_links = True

            comment_text = (
                comment_text + "Here are archived versions to the linked pages.  \n"
            )
            for link in links:
                url_name = link.text
                url = link.get("href")
                archive_url = capture(url)
                comment_text = comment_text + f"* [{url_name}]({archive_url})\n"
        else:
            url = links[0].get("href")

    if not multiple_links:
        url = post.url
        if url.startswith("https://www.reddit.com"):
            url = url[0:8] + "old" + url[11:]
        archive_url = capture(url)
        comment_text = (
            comment_text
            + f"[Here's]({archive_url}) an archived version to the linked page."
        )
    comment_text = comment_text + signature(source_url)
    print(comment_text, file=log_file)
    print(50*"-", file=log_file)
    post.reply(comment_text)
