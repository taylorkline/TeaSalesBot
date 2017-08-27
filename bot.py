import json
import praw
import os
import traceback

# The subreddit that contains the sales
sales_sub = "teasales"
# The subreddit to look for mentions & follow-up with replies
monitor_sub = "tea"

def main():
    reddit = authenticate()
    vendors = load_vendors()
    subscribe(reddit, vendors)

def authenticate():
    return praw.Reddit("teasalesbot")

def load_vendors():
    """
    Loads the vendors from the JSON file, turning all keys to lowercase
    for later string matching.
    """
    with open("./vendors.json") as vendors:
        vendors = json.load(vendors)

    for vendor in vendors:
        vendor["pretty_name"] = vendor["name"]
        for key, val in vendor.items():
            if key == "nicknames":  # nicknames is a list of strings
                for i, nickname in enumerate(val):
                    val[i] = nickname.lower()
            elif key != "pretty_name":  # everything else is a string
                vendor[key] = val.lower()

    return vendors

def subscribe(reddit, vendors):
    sub = reddit.subreddit(monitor_sub)
    streams = [sub.stream.submissions(pause_after=0),
               sub.stream.comments(pause_after=0)]

    stream_idx = 0
    while True:
        for item in streams[stream_idx]:
            if item is None:
                break

            if reddit.config.username == item.author.name:
                continue

            if isinstance(item, praw.models.Submission):
                search_text = f"{item.title} {item.selftext}"
            else:
                search_text = item.body

            vendors_mentioned = get_vendors_mentioned(search_text, vendors)

            if vendors_mentioned:
                try:
                    # Ensure we don't follow-up duplicate times
                    old_id = item.id
                    if already_responded(item, reddit.config.username):
                        continue
                    assert(old_id == item.id)

                    reply = get_reply(reddit, vendors_mentioned)
                    if reply:
                        respond(item, reply)
                except (praw.exceptions.PRAWException, AssertionError) as e:
                    # TODO: Remove AssertionError catch after resolution of
                    #       https://github.com/praw-dev/praw/issues/838
                    print(f"Unable to respond to item {item.id} due to exception:")
                    print(e)
                    traceback.print_exc()

        stream_idx = (stream_idx + 1) % len(streams)

def already_responded(comment_or_submission, bot_username):
    """
    Returns True if we've already responded to this comment or any of its
    parent comments, False otherwise
    """
    if isinstance(comment_or_submission, praw.models.Submission):
        for reply in comment_or_submission.comments:
            if bot_username == reply.author.name:
                return True
        return False

    ancestor = comment_or_submission
    while True:
        ancestor.body
        ancestor.refresh()
        for reply in ancestor.replies:
            if bot_username == reply.author.name:
                return True

        if ancestor.is_root:
            break

        ancestor = ancestor.parent()

    return False

def get_vendors_mentioned(text, vendors):
    """
    Searches through the text for mentions of any of the possible vendors,
    returning a list of vendors which were mentioned.
    """
    text = text.lower()
    mentioned_vendors = []
    for vendor in vendors:
        if vendor["name"] in text:
            mentioned_vendors.append(vendor)
            continue

        ru = "reddit_username"
        if ru in vendor and vendor[ru] in text:
            mentioned_vendors.append(vendor)
            continue

        surl = "store_url"
        if surl in vendor and vendor[surl] in text:
            mentioned_vendors.append(vendor)
            continue

        if "nicknames" in vendor:
            for nickname in vendor["nicknames"]:
                if nickname in text:
                    mentioned_vendors.append(vendor)
                    continue

    return mentioned_vendors

def get_reply(reddit, mentions):
    """
    Creates a table with the appropriate vendor & their sales details.
    Also includes footer with bot information.
    Returns a False-y value if none of the mentioned vendors have active sales.
    """
    rows = ["vendor|sales in /r/TeaSales",
            ":--|:--:"]
    vendors_without_sales = 0
    for vendor in mentions:
        sales = get_recent_sales(reddit, vendor)
        if sales:
            for i, sale in enumerate(sales):
                sale_info = f"|[{create_table_safe_reply(sale.title)}]({sale.url})"
                if i == 0:
                    sale_info = f"{vendor['pretty_name']}{sale_info}"
                else:
                    sale_info = f"|{sale_info}"
                rows.append(sale_info)
        else:
            vendors_without_sales += 1

    if vendors_without_sales == len(mentions):
        return None

    rows = "\n".join(rows)
    footer = "^(TeaSalesBot made with 🍵 and ❤️ by) ^[/u\/taylorkline](/user/taylorkline)"
    return "\n".join([rows, footer])

def create_table_safe_reply(reply):
    return "".join([ch if ch != "|" else "-" for ch in reply])

def get_recent_sales(reddit, vendor):
    """
    Returns the vendor's active sales within the past month, in sorted order by newest sale.
    """
    query = "NOT (flair:expired OR flair:meta)"

    terms = []
    terms.append(create_search_term(vendor["name"]))
    if "reddit_username" in vendor:
        ru = vendor["reddit_username"]
        terms.append(f'author:"{ru}" OR {create_search_term(vendor["reddit_username"])}')
    if "nicknames" in vendor:
        for nickname in vendor["nicknames"]:
            terms.append(create_search_term(vendor["nicknames"]))
    if "store_url" in vendor:
        surl = vendor["store_url"]
        terms.append(f'site:"{surl}" OR {create_search_term(surl)}')

    terms = " OR ".join(terms)
    query = " ".join([query, terms])
    sales = reddit.subreddit(sales_sub).search(query, sort="new", time_filter="month")

    return [sale for sale in sales]

def create_search_term(keyword):
    return f'selftext:"{keyword}" OR title:"{keyword}"'

def respond(comment_or_submission, reply):
    reply = comment_or_submission.reply(reply)

    try:
        prefix = "tmp"
        os.makedirs(f"{prefix}", exist_ok=True)
        fname = f"{reply.id}.log"
        with open(f"{prefix}/{fname}", "w") as logfile:
            logfile.write(reply.body)
            print(f"Response to item {comment_or_submission.id} logged as {fname} in {prefix}/")
    except Exception as e:
        print(f"Did not log response due to exception:\n{e}")

if __name__ == "__main__":
    main()
