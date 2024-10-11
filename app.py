import streamlit as st
import pandas as pd
from get_data.reddit_test import fetch_reddit_data
from nlp.preprocessing import preprocess_text
from nlp.sentiment_analysis import load_model_and_vectorizer, predict_sentiment

def main():
    st.title("Social Media Sentiment Analysis")
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
            data = pd.read_csv('data/collected_data.csv')

            if not data.empty:
                # Load model and vectorizer
                model, vectorizer = load_model_and_vectorizer('models/finalized_model.pkl', 'models/finalized_vectorizer.pkl')

                # Ensure that there are no missing values in the 'processed_content' column
                data = data.dropna(subset=['processed_content'])

                # Predict sentiment
                sentiments = predict_sentiment(data['processed_content'], model, vectorizer)
                data['Sentiment'] = ['Positive' if pred == 1 else 'Negative' for pred in sentiments]

                # Display results
                st.write(data[['processed_content', 'Sentiment']])
                st.success("Sentiment analysis completed.")

                # Optionally save the results
                data[['processed_content', 'Sentiment']].to_csv('data/sentiment_results.csv', index=False)
            else:
                st.error("No preprocessed data available. Please fetch data first.")
        except FileNotFoundError:
            st.error("The data file does not exist. Please fetch and preprocess data first.")
        except Exception as e:
            st.error(f"An error occurred during sentiment analysis: {e}")

if __name__ == "__main__":
    main()
