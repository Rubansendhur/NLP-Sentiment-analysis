import praw
import pandas as pd
from datetime import datetime, timedelta

# Set up Reddit API credentials
reddit = praw.Reddit(client_id='bDicYJSIXzQh_wUqYhLtdg',
                     client_secret='KVvJ9dhgi-LaC33s3sJ5eUoqw7A1_Q',
                     user_agent='my_sentiment_analyzer:v1.0.0 (by /u/Ok_Cook_8674)')

def fetch_reddit_data(brand_name, limit=1000, days=14):
    subreddit = reddit.subreddit('all')  # Searching across all subreddits
    posts = []
    time_threshold = datetime.now() - timedelta(days=days)

    # Search for posts related to the user input (brand or topic)
    try:
        for post in subreddit.search(brand_name, sort='hot', time_filter='all', limit=limit):
            post_time = datetime.utcfromtimestamp(post.created_utc)
            
            # Filter out older posts based on time threshold
            if post_time >= time_threshold:
                post_content = post.selftext if hasattr(post, 'selftext') else None

                # Append post data
                posts.append([
                    post.title,
                    post_content,  # Use selftext to retrieve the post body
                    post.score,
                    post.id,
                    post.subreddit.display_name,  # Get the subreddit name
                    post.url,
                    post.num_comments,
                    post_time
                ])
    except Exception as e:
        print(f"Failed to fetch data due to: {e}")

    # Return the data as a DataFrame
    return pd.DataFrame(posts, columns=['Title', 'content', 'Score', 'ID', 'Subreddit', 'URL', 'Comments', 'Created'])
