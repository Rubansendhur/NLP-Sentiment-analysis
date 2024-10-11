import time
from ntscraper import Nitter
from datetime import datetime, timedelta
import pandas as pd

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

# Function to fetch brand-related tweets
def get_recent_brand_related_posts(brand_name, mode='term', number=10, language='en', days=14):
    attempt = 0
    instance_index = 0
    time_threshold = datetime.now() - timedelta(days=days)  # Filter for past two weeks
    tweet_data_list = []

    while attempt < 3:
        try:
            if instance_index == -1:
                print("No more instances available. Exiting...")
                return pd.DataFrame()  # Return an empty DataFrame if all instances are exhausted

            search_query = f"{brand_name}"  # User input dynamically passed into the search query
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
            for tweet in tweets.get('tweets', []):
                tweet_text = tweet.get("text", "").strip()
                tweet_date = tweet.get("date", "No date available")

                try:
                    tweet_date_dt = datetime.strptime(tweet_date, "%b %d, %Y · %I:%M %p %Z")
                    if tweet_date_dt >= time_threshold:
                        tweet_data = {
                            "username": tweet.get("user", {}).get("username", "N/A"),
                            "content": tweet_text,
                            "date": tweet_date_dt.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        tweet_data_list.append(tweet_data)
                except ValueError as e:
                    print(f"Error parsing tweet date: {e}")

            if tweet_data_list:
                return pd.DataFrame(tweet_data_list)

        except Exception as e:
            print(f"Error: {e}")
            if "rate limited" in str(e):
                attempt += 1
                instance_index = switch_instance(instance_index)
                time.sleep(15)  # Increase wait time if rate-limited
            else:
                break

    return pd.DataFrame()  # Return an empty DataFrame if no data fetched
