import time
from ntscraper import Nitter
from datetime import datetime, timedelta

# List of Nitter instances
nitter_instances = [
    #"https://nitter.unixfox.eu",
    #"https://nitter.lacontrevoie.fr",
    #"https://nitter.pussthecat.org",
    "https://nitter.net",
    "https://nitter.fdn.fr",
    "https://nitter.privacydev.net",
    "https://nitter.patthor.net",
    "https://nitter.bus-hit.me",
    "https://nitter.moomoo.me",
    "https://nitter.13ad.de",
]

# Scraper setup
scraper = Nitter(log_level=1, skip_instance_check=False)

# Function to switch Nitter instance if rate-limited
def switch_instance(current_index):
    new_index = (current_index + 1) % len(nitter_instances)
    if new_index == current_index:
        print("All Nitter instances have been exhausted.")
        return -1
    print(f"Switched to new Nitter instance: {nitter_instances[new_index]}")
    return new_index

from datetime import datetime, timedelta

# Modify the function to filter tweets by date
def get_recent_brand_related_posts(brand_name, mode='term', number=10, language='en', days=14):
    attempt = 0
    instance_index = 0
    time_threshold = datetime.now() - timedelta(days=days)  # Filter for past two weeks
    while attempt < 3:
        try:
            if instance_index == -1:
                print("No more instances available. Exiting...")
                return []

            search_query = f"{brand_name}"
            tweets = scraper.get_tweets(
                search_query, 
                mode=mode, 
                number=number, 
                language=language, 
                instance=nitter_instances[instance_index]
            )

            print("Raw tweet data:")
            print(tweets)

            # Process fetched tweets
            recent_tweets = []
            for tweet in tweets.get('tweets', []):
                tweet_text = tweet.get("text", "").strip()
                tweet_date = tweet.get("date", "No date available")

                # Convert tweet_date to a datetime object and filter
                try:
                    tweet_date_dt = datetime.strptime(tweet_date, "%b %d, %Y · %I:%M %p %Z")
                    if tweet_date_dt < time_threshold:
                        continue  # Skip older tweets
                except Exception as e:
                    print(f"Error parsing tweet date: {e}")
                    continue

                if tweet_text and tweet_text != "No content available":
                    tweet_data = {
                        "username": tweet.get("user", {}).get("username", "N/A"),
                        "tweet_content": tweet_text,
                        "date": tweet_date
                    }
                    recent_tweets.append(tweet_data)

            recent_tweets.sort(key=lambda x: x['date'], reverse=True)
            return recent_tweets[:number]

        except Exception as e:
            print(f"Error: {e}")
            if "rate limited" in str(e):
                attempt += 1
                instance_index = switch_instance(instance_index)
                if instance_index == -1:
                    break
                time.sleep(15)  # Increase wait time to 15 seconds
            else:
                break

    return []


# Example usage
if __name__ == "__main__":
    brand_name = "nike"  # Specify the brand/topic you're interested in
    mode = 'term'  # Search mode: 'term' for a general keyword search
    
    posts = get_recent_brand_related_posts(brand_name, mode=mode, number=10)
    
    # Print fetched tweets
    for post in posts:
        print(f"Username: {post['username']}")
        print(f"Tweet: {post['tweet_content']}")
        print("-" * 80)
