from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from random import randint
from itertools import product, chain
from typing import List

import praw
from archivenow import archivenow
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


def reply_to_missed(
    reddit,
    subreddit,
    log_files: List[TextIOWrapper],
    number_limit=None,
    time_limit=None,
):
    log = lambda s: [print(s, file=log_file) for log_file in log_files]
    count = 0
    submissions = subreddit.new(limit=number_limit)

    now = datetime.utcnow()

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
            submission.reply(reply_text(submission, log_files))
            count += 1
    if count == 0:
        log("No submissions found.")
    else:
        log(f"{count} submission{{}} found.".format("s" if count > 1 else ""))


REDDIT_PREFIXES = list(
    map(
        lambda t: t[0] + t[1],
        product(
            ["https://", "http://"],
            ["www.reddit.com", "i.reddit.com", "old.reddit.com", "reddit.com",],
        ),
    )
)


def is_reddit_link(l: str) -> bool:
    return any(map(lambda prefix: l.startswith(prefix), REDDIT_PREFIXES))


def reply_text(post: Submission, log_files: List[TextIOWrapper]) -> str:
    log = lambda s: [print(s, file=log_file) for log_file in log_files]
    log("\n" + 79 * "-")
    log(f" - Title: {post.title}")
    quote, source_url = witty_quote()
    comment_text = f"{quote}\n\n"
    multiple_links = False

    if post.is_self:
        log(" · Self post")
        text = post.selftext
        document = etree.fromstring(f"<items>{markdown(text)}</items>")
        links = document.xpath("//a")
        raw_links = [
            w.rstrip(",.:;")
            for w in text.split()
            if w.startswith("https://") or w.startswith("http://")
        ]
        if not links and not raw_links:
            log(" · No links found")
            return

        elif len(links) + len(raw_links) > 1:
            log(" · Found multipe links")
            multiple_links = True

            comment_text = comment_text + "Here are snapshots of the linked pages.  \n"

            for link in raw_links:
                url_name = link
                url = link
                if is_reddit_link(url):
                    url = "https://old." + url[url.find("reddit") :]
                archive_url = archivenow.push(url, "ia")[0]
                if archive_url.startswith("https://"):
                    comment_text = comment_text + f"* [{url_name}]({archive_url})\n"
            for link in links:
                url_name = link.text
                url = link.get("href")
                archive_url = archivenow.push(url, "ia")[0]
                if archive_url.startswith("https://"):
                    comment_text = comment_text + f"* [{url_name}]({archive_url})\n"

        elif len(links) == 1:
            log(" · Found single link")
            url = links[0].get("href")
        else:
            log(" · Found single link")
            url = raw_links[0]

    if not multiple_links:
        url: str = post.url

        if is_reddit_link(url):
            url = "https://old." + url[url.find("reddit") :]
        archive_url = archivenow.push(url, "ia")[0]
        if archive_url.startswith("https://"):
            comment_text = (
                comment_text + f"[Here's]({archive_url}) a snapshot of the linked page."
            )
    comment_text = comment_text + signature(source_url)
    log(f" - Comment text:\n{comment_text}")
    return comment_text
