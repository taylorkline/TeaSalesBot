import json
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
                comment.refresh()
                responders = [reply.author.name for reply in comment.replies.list()]
                if reddit.config.username in responders:
                    continue

                reply = get_reply(reddit, vendors_mentioned)
                respond(comment, reply)
            except praw.exceptions.PRAWException as e:
                print("Unable to respond to comment {comment.id} due to exception:\n{e}")

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
    """
    rows = ["vendor|sales",
            ":--|:--:"]
    for vendor in mentions:
        sales = get_recent_sales(reddit, vendor)
        if sales:
            for i, sale in enumerate(sales):
                if i == 0:
                    sale_info = f"{vendor['pretty_name']}|[{sale.title}]({sale.url})"
                else:
                    sale_info = f"||[{sale.title}]({sale.url})"
                rows.append(sale_info)
        else:
            sales = f"No unexpired sales posted to /r/{sales_sub} within the past 30 days"
            rows.append(f"{vendor['pretty_name']}|{sales}")

    footer = "^(TeaSalesBot made with 🍵 and ❤️ by /u/taylorkline)"
    return "\n".join(["\n".join(rows), footer])

def get_recent_sales(reddit, vendor):
    """
    Returns the vendor's active sales within the past month, in sorted order by newest sale.
    """
    query = "NOT (flair:expired OR flair:meta)"

    terms = []
    for k,v in vendor.items():
        if k == "nicknames":
            terms.extend(f"\"{nickname}\"" for nickname in v)
        else:
            assert(isinstance(v, str))
            terms.append(f"\"{v}\"")

    terms = " OR ".join(terms)
    query = " ".join([query, terms])
    sales = [sale for sale in
             reddit.subreddit(sales_sub).search(query, sort="new", time_filter="month")]
    pretty_sales = "\n".join([sale.title for sale in sales])

    print(f"BEGINSALES\nsearch for:\n{query}\nreturned {len(sales)} sales:\n{pretty_sales}\n"
           "ENDSALES\n")

    return sales

def respond(comment, reply):
    comment.reply(reply)

if __name__ == "__main__":
    main()
