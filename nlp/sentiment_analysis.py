import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import streamlit as st

# Load model and vectorizer
def load_model_and_vectorizer(model_path, vectorizer_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer

# Predict the sentiment of text using the loaded model and vectorizer
def predict_sentiment(texts, model, vectorizer):
    # Ensure input is in list format
    if isinstance(texts, str):
        texts = [texts]  # Convert a single string to a list of one string
    text_vector = vectorizer.transform(texts)
    return model.predict(text_vector)

def analyze_sentiments(data, model, vectorizer):
    # Predict sentiment
    sentiments = predict_sentiment(data['processed_content'].tolist(), model, vectorizer)
    data['Sentiment'] = ['Positive' if pred == 1 else 'Negative' for pred in sentiments]

    # Calculate overall results
    positive_count = data['Sentiment'].value_counts().get('Positive', 0)
    negative_count = data['Sentiment'].value_counts().get('Negative', 0)
    total_count = positive_count + negative_count

    positive_percentage = (positive_count / total_count) * 100 if total_count > 0 else 0
    negative_percentage = (negative_count / total_count) * 100 if total_count > 0 else 0

    # Display overall results
    result_df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative'],
        'Count': [positive_count, negative_count],
        'Percentage': [positive_percentage, negative_percentage]
    })
    
    st.write("Sentiment analysis completed.")
    st.write(data[['processed_content', 'Sentiment']])
    st.write("Overall Results:")
    st.table(result_df)

    # Optionally save the results
    data[['processed_content', 'Sentiment']].to_csv('data/sentiment_results.csv', index=False)

# The main function would be used within your Streamlit app and not here.
# It should handle loading data, calling this analysis function, etc.
