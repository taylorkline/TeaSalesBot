import json
import pdb
import praw

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
        for key, val in vendor.items():
            if key == "nicknames":  # nicknames is a list of strings
                for i, nickname in enumerate(val):
                    val[i] = nickname.lower()
            else:  # everything else is a string
                vendor[key] = val.lower()

    return vendors

def subscribe(reddit, vendors):
    for comment in reddit.subreddit(monitor_sub).stream.comments():
        if reddit.config.username == comment.author.name:
            continue

        vendors_mentioned = get_vendors_mentioned(comment.body, vendors)

        if vendors_mentioned:
            # Ensure we don't follow-up duplicate times
            comment.refresh()
            responders = [reply.author.name for reply in comment.replies.list()]
            if reddit.config.username in responders:
                continue

            reply = get_reply(reddit, vendors_mentioned)
            respond(comment, reply)

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

def get_reply(mentions):
    """
    Creates a table with the appropriate vendor & their sales details.
    Also includes footer with bot information.
    """
    pass

def get_recent_sales(reddit, vendor):
    pass

def respond(reddit, comment_id, reply):
    pass

if __name__ == "__main__":
    main()
