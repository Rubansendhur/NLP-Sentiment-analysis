import pandas as pd
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.chunk import RegexpParser
from textblob import TextBlob
from transformers import BertTokenizer, BertModel
import torch

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

# Load the English NLP model for spaCy
nlp = spacy.load('en_core_web_sm')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
# Download required NLTK packages

def apply_spacy_nlp(text):
    """Apply spaCy NLP to extract detailed POS, dependencies, and named entities."""
    doc = nlp(str(text))
    pos_tags = " ".join([f"{token.text}/{token.pos_}" for token in doc])
    deps = " ".join([f"{token.text}/{token.dep_}" for token in doc])
    entities = [(ent.text, ent.label_) for ent in doc.ents]  # Enhanced entity extraction
    return pos_tags, deps, entities

def textblob_pos(text):
    """Use TextBlob for additional POS tagging."""
    blob = TextBlob(str(text))
    return " ".join([f"{word}/{pos}" for word, pos in blob.tags])

def identify_important_words(text):
    """Identify important words (noun phrases) in sentences."""
    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(text)
    important_words = []
    
    for sentence in sentences:
        words = word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        
        # Define a grammar for chunking (looking for noun phrases)
        grammar = "NP: {<DT>?<JJ>*<NN>}"
        cp = RegexpParser(grammar)
        tree = cp.parse(tagged)
        
        # Traverse the chunk tree to identify noun phrases
        for subtree in tree.subtrees():
            if subtree.label() == 'NP':
                noun_phrase = " ".join(word for word, tag in subtree.leaves() if word not in stop_words)
                important_words.append(noun_phrase)
    
    # Return the most important noun phrase (or the first one if there are multiple)
    return important_words[0] if important_words else None

def tokenize_words(text):
    """Tokenize text into words and return a few sample tokens."""
    tokens = word_tokenize(text)
    # Display a few tokens
    return tokens[:10]  # Adjust the slice as needed to display more or fewer tokens

def syntax_analysis(file_path):
    """Perform syntax analysis including tokenization, POS tagging, chunking, and important word identification."""
    df = pd.read_csv(file_path)
    df['cleaned_content'] = df['cleaned_content'].astype(str)

    # Tokenize into sentences using NLTK
    df['Sentences'] = df['cleaned_content'].apply(sent_tokenize)

    # Apply spaCy NLP for POS tagging, dependencies, and named entities
    df[['POS_spacy', 'Dependencies', 'Entities']] = df['cleaned_content'].apply(
        lambda text: pd.Series(apply_spacy_nlp(text))
    )
    
    # Convert Entities list to a more readable format
    df['Entities'] = df['Entities'].apply(lambda entities: ', '.join([f"{text} ({label})" for text, label in entities]))
    
    # Additional POS tagging using TextBlob
    df['POS_textblob'] = df['cleaned_content'].apply(textblob_pos)

    # Identify the most important word in each sentence
    df['Important_Word'] = df['cleaned_content'].apply(identify_important_words)

    # Extract and display tokenized words
    df['Tokenized_Words'] = df['cleaned_content'].apply(tokenize_words)

    # Print a sample of the results to the terminal including tokenized words
    print(df[['cleaned_content', 'Sentences', 'POS_spacy', 'Dependencies', 'Entities', 'POS_textblob', 'Important_Word', 'Tokenized_Words']].head())

    # Save to a CSV file to showcase results
    df.to_csv('E:\\cit-22smcb0055\\SEM-V\\NLP\\project\\env\\nlp senti\\syntax_analysis_results.csv', index=False)



if __name__ == "__main__":
    # Provide the path to your cleaned data
    data_path = 'E:\\cit-22smcb0055\\SEM-V\\NLP\\project\\env\\nlp senti\\cleaned_data.csv'
    syntax_analysis(data_path)
