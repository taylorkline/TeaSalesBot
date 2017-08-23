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
    pass

def subscribe(reddit, vendors):
    for comment in reddit.subreddit(monitor_sub).stream.comments():
        vendors_mentioned = get_vendors_mentioned(comment.body, vendors)
        if vendors_mentioned:
            reply = get_reply(vendors_mentioned)
            respond(reddit, comment.id, reply)

def get_reply(mentions):
    """
    Creates a table with the appropriate vendor & their sales details.
    Also includes footer with bot information.
    """
    pass

def get_vendors_mentioned(text, vendors):
    """
    Searches through the text for mentions of any of the possible vendors,
    returning a list of vendors which were mentioned.
    """
    # TODO: Iterate vendors looking for matches in the text
    pass

if __name__ == "__main__":
    main()
