import json
import praw
import os

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
    for comment in reddit.subreddit(monitor_sub).stream.comments():
        if reddit.config.username == comment.author.name:
            continue

        vendors_mentioned = get_vendors_mentioned(comment.body, vendors)

        if vendors_mentioned:
            try:
                # Ensure we don't follow-up duplicate times
                if already_responded(comment, reddit.config.username):
                    continue

                reply = get_reply(reddit, vendors_mentioned)
                if reply:
                    respond(comment, reply)
            except praw.exceptions.PRAWException as e:
                print("Unable to respond to comment {comment.id} due to exception:\n{e}")

def already_responded(comment, bot_username):
    """
    Returns True if we've already responded to this comment or any of its
    parent comments, False otherwise
    """
    ancestor = comment
    while True:
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

def respond(comment, reply):
    reply = comment.reply(reply)

    try:
        prefix = "tmp"
        os.makedirs(f"{prefix}", exist_ok=True)
        fname = f"{reply.id}.log"
        with open(f"{prefix}/{fname}", "w") as logfile:
            logfile.write(reply.body)
            print(f"Response to comment {comment.id} logged as {fname} in {prefix}/")
    except Exception as e:
        print(f"Did not log response due to exception:\n{e}")

if __name__ == "__main__":
    main()
