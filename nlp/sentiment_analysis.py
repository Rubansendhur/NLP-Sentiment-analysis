import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

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

def analyze_sentiments(data_path, model_path, vectorizer_path):
    # Load preprocessed data
    data = pd.read_csv(data_path)
    if 'processed_content' not in data.columns:
        raise ValueError("The required column 'processed_content' is missing in the data.")

    # Load model and vectorizer
    model, vectorizer = load_model_and_vectorizer(model_path, vectorizer_path)
    
    # Ensure that there are no missing values in the 'processed_content' column
    data = data.dropna(subset=['processed_content'])
    
    # Predict sentiment
    sentiments = predict_sentiment(data['processed_content'], model, vectorizer)
    data['Sentiment'] = ['Positive' if pred == 1 else 'Negative' for pred in sentiments]
    
    return data

# Example usage
if __name__ == "__main__":
    data_path = 'data\collected_data.csv'
    model_path = 'models\finalized_model.pkl'
    vectorizer_path = 'models\finalized_vectorizer.pkl'
    
    result_data = analyze_sentiments(data_path, model_path, vectorizer_path)
    result_data.to_csv('path/to/save/sentiment_results.csv', index=False)
    print("Sentiment analysis completed and results saved.")