import praw
import pandas as pd
from datetime import datetime, timedelta

# Set up Reddit API credentials
reddit = praw.Reddit(client_id='bDicYJSIXzQh_wUqYhLtdg',
                     client_secret='KVvJ9dhgi-LaC33s3sJ5eUoqw7A1_Q',
                     user_agent='my_sentiment_analyzer:v1.0.0 (by /u/Ok_Cook_8674)')

# Define a function to fetch posts from a subreddit
def fetch_reddit_data(brand_name, limit=100, days=14):
    subreddit = reddit.subreddit('all')  # Searching across all subreddits
    posts = []
    time_threshold = datetime.now() - timedelta(days=days)

    # Search for posts related to the user input (brand or topic)
    for post in subreddit.search(brand_name, sort='hot', time_filter='all', limit=limit):
        post_time = datetime.utcfromtimestamp(post.created_utc)
        if post_time < time_threshold:
            continue  # Skip older posts

        posts.append([
            post.title, 
            post.selftext, 
            post.score, 
            post.id, 
            post.subreddit, 
            post.url, 
            post.num_comments, 
            post_time, 
            post.body if hasattr(post, 'body') else None
        ])
        
    return pd.DataFrame(posts, columns=['Title', 'Body', 'Score', 'ID', 'Subreddit', 'URL', 'Comments', 'Created', 'Post Content'])
