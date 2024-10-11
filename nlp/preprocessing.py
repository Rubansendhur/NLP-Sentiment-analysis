import pandas as pd
import re
from nlp_preprocess_toolkit_utils import preprocess_text  # Ensure this is correctly imported
import streamlit as st  

def twitter_specific_preprocessing(text):
    """Clean Twitter data."""
    text = re.sub(r'@\w+', '', text)  # Remove handles
    text = re.sub(r'#(\S+)', r'\1', text)  # Remove hashtags but keep text
    text = re.sub(r'\brt\b', '', text, flags=re.IGNORECASE)  # Remove RT symbols
    text = re.sub(r'https?://\S+', '', text)  # Remove URLs
    text = re.sub(r'\b\d+\b', '', text)  # Remove numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Keep only letters and spaces
    return text.strip()

def reddit_specific_preprocessing(text):
    """Clean Reddit data."""
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove markdown links
    text = re.sub(r'https?://\S+', '', text)  # Remove URLs
    text = re.sub(r'&\w+;', '', text)  # Remove HTML entities
    text = re.sub(r'\b\d+\b', '', text)  # Remove numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Keep only letters and spaces
    return text.strip()

def preprocess_and_save(data_frame):
    # Handle missing values: Replace NaNs with an empty string
    data_frame['Content'].fillna("", inplace=True)

    # Apply initial preprocessing using the custom library
    data_frame['cleaned_content'] = data_frame['Content'].apply(preprocess_text)

    # Apply platform-specific cleaning based on the 'Platform' column
    data_frame['cleaned_content'] = data_frame.apply(
        lambda row: twitter_specific_preprocessing(row['cleaned_content']) if row['Platform'] == 'Twitter'
        else reddit_specific_preprocessing(row['cleaned_content']), axis=1
    )