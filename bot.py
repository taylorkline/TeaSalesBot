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
        # TODO: Ensure we have not already responded to this comment
        vendors_mentioned = get_vendors_mentioned(comment.body, vendors)
        if vendors_mentioned:
            reply = get_reply(vendors_mentioned)
            respond(reddit, comment.id, reply)

def get_vendors_mentioned(text, vendors):
    """
    Searches through the text for mentions of any of the possible vendors,
    returning a list of vendors which were mentioned.
    """
    # TODO: Iterate vendors looking for matches in the text
    pass

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
