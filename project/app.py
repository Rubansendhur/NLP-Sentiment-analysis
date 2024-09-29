from flask import Flask, request, render_template, flash, redirect, url_for
from twitter_nitter import get_recent_brand_related_posts  # Import your Twitter scraper function
from reddit_test import fetch_reddit_data  # Import your Reddit scraper function

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

@app.route('/', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # Get user input from the form
        brand_name = request.form.get('text', '').strip()  # Safely get and strip user input
        
        if not brand_name:
            # If the input is empty, show a warning and redirect to the form
            flash("Please enter a brand or topic to analyze.", "warning")
            return redirect(url_for('analyze'))
        
        try:
            # Fetch recent Twitter posts related to the input
            twitter_posts = get_recent_brand_related_posts(brand_name, number=10, days=14)

            # Fetch recent Reddit posts related to the input
            reddit_posts = fetch_reddit_data(brand_name, limit=100, days=14)

            # If no data found
            if not twitter_posts and reddit_posts.empty:
                flash(f"No data found for '{brand_name}'. Try a different brand or topic.", "info")
                return redirect(url_for('analyze'))

            # Pass the data to the results template to display the fetched data
            return render_template('results.html', twitter_posts=twitter_posts, reddit_posts=reddit_posts)

        except Exception as e:
            flash(f"An error occurred while fetching data: {e}", "danger")
            return redirect(url_for('analyze'))

    # Render the input form
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
