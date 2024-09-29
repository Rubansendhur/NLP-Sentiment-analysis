import praw
import pandas as pd
from datetime import datetime, timedelta

# Set up Reddit API credentials
reddit = praw.Reddit(client_id='bDicYJSIXzQh_wUqYhLtdg',
                     client_secret='KVvJ9dhgi-LaC33s3sJ5eUoqw7A1_Q',
                     user_agent='my_sentiment_analyzer:v1.0.0 (by /u/Ok_Cook_8674)')

# Define a function to fetch posts from a subreddit
def fetch_reddit_data(subreddit_name, limit=100, days=14):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    time_threshold = datetime.now() - timedelta(days=days)
    
    for post in subreddit.hot(limit=limit):
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

# Example: Fetch posts from the past two weeks
subreddit_data = fetch_reddit_data('nike', limit=100, days=14)
print(subreddit_data.head())
