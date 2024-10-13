import streamlit as st
import pandas as pd
import os
from get_data.reddit_test import fetch_reddit_data
from nlp.preprocessing import preprocess_text
from nlp.sentiment_analysis import load_model_and_vectorizer, analyze_sentiments

def main():
    st.title("😐Sentiment Analysis FOr Brand and topic insights!☹️")
    query = st.text_input("Enter a topic or brand:")

    if st.button("Get Data"):
        if query:
            try:
                # Fetch data from Reddit
                reddit_posts = fetch_reddit_data(query)  # This should return a DataFrame
                if isinstance(reddit_posts, pd.DataFrame) and not reddit_posts.empty:
                    reddit_posts['Source'] = 'Reddit'  # Add a source column

                    # Use title if content is empty
                    reddit_posts['content_to_process'] = reddit_posts.apply(
                        lambda row: row['content'] if pd.notna(row['content']) and row['content'].strip() != '' else row['Title'],
                        axis=1
                    )

                    # Preprocess data
                    reddit_posts['processed_content'] = reddit_posts['content_to_process'].apply(preprocess_text)
                    reddit_posts.to_csv('data/collected_data.csv', index=False)
                    st.success("Data fetched from Reddit, processed, and saved successfully!")
                else:
                    st.warning("No data fetched from Reddit. Please try a different query or check your network.")
            except Exception as e:
                st.error(f"Failed to fetch or preprocess data: {e}")

    if st.button("Analyze Sentiment"):
        try:
            # Load preprocessed data
            data_path = 'data/collected_data.csv'
            if os.path.exists(data_path):
                data = pd.read_csv(data_path)

                if not data.empty:
                    # Load model and vectorizer
                    model, vectorizer = load_model_and_vectorizer('models/finalized_model.pkl', 'models/finalized_vectorizer.pkl')

                    # Ensure that there are no missing values in the 'processed_content' column
                    data = data.dropna(subset=['processed_content'])

                    # Perform sentiment analysis
                    analyze_sentiments(data, model, vectorizer)
                else:
                    st.error("No preprocessed data available. Please fetch data first.")
            else:
                st.error("The data file does not exist. Please fetch and preprocess data first.")
        except Exception as e:
            st.error(f"An error occurred during sentiment analysis: {e}")

if __name__ == "__main__":
    main()
