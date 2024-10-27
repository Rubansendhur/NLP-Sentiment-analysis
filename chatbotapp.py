import streamlit as st
import pandas as pd
import os
import spacy
from transformers import pipeline
from textblob import TextBlob
from fuzzywuzzy import fuzz, process
import language_tool_python
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Load necessary resources
nlp = spacy.load("en_core_web_sm")
conversation_pipeline = pipeline('text-generation', model='gpt2')

from get_data.reddit_test import fetch_reddit_data
from nlp.preprocessing import preprocess_text
from nlp.sentiment_analysis import load_model_and_vectorizer, analyze_sentiments, predict_sentiment

# Initialize stopwords and grammar tool
stop_words = set(stopwords.words('english'))
tool = language_tool_python.LanguageTool('en-US')

# List of common brands to fuzzy match against
common_brands = ['Nike', 'Apple', 'Lenovo', 'Samsung', 'Google', 'Microsoft', 'Adidas', 'Dell', 'HP', 'Sony', 'Puma','Vivo','Oppo','Oneplus']

# Helper function to correct grammar and spelling mistakes using language_tool_python
def correct_spelling_and_grammar(text):
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text

# Helper function to extract multiple brand names using fuzzy matching
def extract_brands(text):
    corrected_text = correct_spelling_and_grammar(text)  # Correct the input first
    extracted_brands = []
    for brand in common_brands:
        if fuzz.partial_ratio(corrected_text, brand) >= 75:  # High confidence threshold for matching
            extracted_brands.append(brand)
    return extracted_brands

# Helper function to perform syntactic analysis
def perform_syntax_analysis(text):
    corrected_text = correct_spelling_and_grammar(text)  # Correct minor spelling errors
    tokens = nltk.pos_tag(word_tokenize(corrected_text))
    return tokens, corrected_text

# Chatbot logic for processing input
def chatbot_response(user_input):
    # Handle greetings
    if any(greet in user_input.lower() for greet in ['hi', 'hello', 'hey']):
        return "Hello! How can I assist you today? You can ask about the sentiment for a brand."

    # Perform brand extraction using fuzzy matching
    brands = extract_brands(user_input)

    if brands:
        # If brands are detected, perform sentiment analysis for each brand
        return fetch_and_analyze_sentiment(brands)
    else:
        # No brands found, fallback to a conversational response
        response = conversation_pipeline(user_input, max_length=50)
        return response[0]['generated_text']

# Function to fetch and analyze sentiment and display friendly insights for multiple brands
def fetch_and_analyze_sentiment(brands):
    insights = []
    for brand in brands:
        try:
            # Fetch data from Reddit using the detected brand
            reddit_posts = fetch_reddit_data(brand)
            if isinstance(reddit_posts, pd.DataFrame) and not reddit_posts.empty:
                reddit_posts['Source'] = 'Reddit'

                # Preprocess data
                reddit_posts['content_to_process'] = reddit_posts.apply(
                    lambda row: row['content'] if pd.notna(row['content']) and row['content'].strip() != '' else row['Title'],
                    axis=1
                )
                reddit_posts['processed_content'] = reddit_posts['content_to_process'].apply(preprocess_text)

                # Save for debugging
                reddit_posts.to_csv(f'data/collected_data_{brand}.csv', index=False)

                # Load model and vectorizer
                model, vectorizer = load_model_and_vectorizer('models/finalized_model.pkl', 'models/finalized_vectorizer.pkl')

                # Ensure no missing values
                reddit_posts = reddit_posts.dropna(subset=['processed_content'])

                # Perform sentiment analysis
                sentiments = predict_sentiment(reddit_posts['processed_content'].tolist(), model, vectorizer)
                reddit_posts['Sentiment'] = ['Positive' if pred == 1 else 'Negative' for pred in sentiments]

                # Add insights for this brand
                insights.append(generate_sentiment_insights(reddit_posts, brand))
            else:
                insights.append(f"Sorry, no relevant data could be fetched for {brand}.")
        except Exception as e:
            insights.append(f"Error during sentiment analysis for {brand}: {str(e)}")
    
    # Return combined insights for all brands
    return "\n\n".join(insights)

# Function to generate friendly sentiment insights for each brand
def generate_sentiment_insights(data, brand):
    total_count = len(data)
    positive_count = data['Sentiment'].value_counts().get('Positive', 0)
    negative_count = data['Sentiment'].value_counts().get('Negative', 0)

    positive_percentage = (positive_count / total_count) * 100 if total_count > 0 else 0
    negative_percentage = (negative_count / total_count) * 100 if total_count > 0 else 0

    # Generate a conversational summary for the brand
    summary = (
        f"Sentiment analysis for **{brand}**:\n\n"
        f"- Positive mentions: **{positive_count}** ({positive_percentage:.2f}%)\n"
        f"- Negative mentions: **{negative_count}** ({negative_percentage:.2f}%)\n\n"
    )

    if positive_percentage > negative_percentage:
        summary += f"Overall, the sentiment towards **{brand}** is **mostly positive**. 🎉"
    elif negative_percentage > positive_percentage:
        summary += f"Overall, the sentiment towards **{brand}** is **mostly negative**. 😟"
    else:
        summary += f"The sentiment is **mixed** with equal parts positive and negative mentions for **{brand}**. 🤔"

    return summary

# Syntax and semantics analysis before sentiment analysis
def syntax_semantics_analysis(user_input):
    try:
        # Perform syntax analysis (POS tagging and chunking)
        tokens, corrected_text = perform_syntax_analysis(user_input)
        blob = TextBlob(corrected_text)
        pos_tags = " ".join([f"{word}/{tag}" for word, tag in blob.tags])

        # Return syntactic and semantic info
        return f"Syntactic Analysis: {tokens}, POS tags: {pos_tags}, Corrected Text: {corrected_text}"
    except Exception as e:
        return f"Error during syntax and semantics analysis: {str(e)}"

# Main Streamlit App
def main():
    st.title("💬 Sentiment Analysis Chatbot 🤖")

    # User input box
    user_input = st.text_input("Ask me about any brands or topics, and I'll analyze the sentiment for you:")

    if st.button("Send"):
        if user_input:
            # Perform syntax and semantics analysis first
            syntax_result = syntax_semantics_analysis(user_input)
            st.write("### Syntax and Semantics Analysis")
            st.write(syntax_result)

            # Get the chatbot's response
            response = chatbot_response(user_input)
            st.write(f"### Bot Response:")
            st.write(f"Bot: {response}")
        else:
            st.write("Please type something to get started.")

# Run Streamlit app
if __name__ == "__main__":
    main()
