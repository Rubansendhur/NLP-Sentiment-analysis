import pandas as pd
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.chunk import RegexpParser
from textblob import TextBlob
from transformers import BertTokenizer, BertModel
import torch

# Pre-load necessary resources
nlp = spacy.load('en_core_web_sm')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

# Define Chunking grammar for Noun Phrases (NP) and Verb Phrases (VP)
chunk_grammar = """
    NP: {<DT>?<JJ>*<NN>}   # Noun Phrase
    VP: {<VB.*><NP|PP>*}   # Verb Phrase
"""

def apply_spacy_nlp(text):
    """Extract POS, dependencies, and named entities using spaCy."""
    doc = nlp(text)
    pos_tags = " ".join([f"{token.text}/{token.pos_}" for token in doc])
    deps = " ".join([f"{token.text}/{token.dep_}" for token in doc])
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return pos_tags, deps, entities

def get_bert_embeddings(text):
    """Generate BERT embeddings for the given text."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings.tolist()

def chunk_text(text):
    """Perform chunking on the text using NLTK and extract noun and verb phrases."""
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    chunk_parser = RegexpParser(chunk_grammar)
    tree = chunk_parser.parse(pos_tags)
    
    # Extract noun phrases (NP) and verb phrases (VP)
    noun_phrases = []
    verb_phrases = []
    
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            noun_phrases.append(" ".join(word for word, tag in subtree.leaves()))
        elif subtree.label() == 'VP':
            verb_phrases.append(" ".join(word for word, tag in subtree.leaves()))
    
    return noun_phrases, verb_phrases

def syntax_and_semantics_analysis(file_path):
    """Perform combined syntax and semantics analysis on textual data."""
    try:
        df = pd.read_csv(file_path)
        df['cleaned_content'] = df['cleaned_content'].astype(str)

        # Apply spaCy NLP, TextBlob, and BERT embeddings
        df['SpaCy_analysis'] = df['cleaned_content'].apply(apply_spacy_nlp)
        df['BERT_embeddings'] = df['cleaned_content'].apply(get_bert_embeddings)
        df[['POS_spacy', 'Dependencies', 'Entities']] = pd.DataFrame(df['SpaCy_analysis'].tolist(), index=df.index)
        df['Entities'] = df['Entities'].apply(lambda x: ', '.join([f"{e[0]} ({e[1]})" for e in x]))

        # Additional POS tagging and tokenization using NLTK and TextBlob
        df['POS_textblob'] = df['cleaned_content'].apply(lambda text: " ".join([f"{word}/{pos}" for word, pos in TextBlob(text).tags]))
        df['Tokenized_Words'] = df['cleaned_content'].apply(lambda text: word_tokenize(text)[:10])

        # Apply chunking to extract noun and verb phrases
        df[['Noun_Phrases', 'Verb_Phrases']] = df['cleaned_content'].apply(
            lambda text: pd.Series(chunk_text(text))
        )

        df.to_csv('syntax_semantics_analysis_results.csv', index=False)
        print("Analysis completed and saved to 'syntax_semantics_analysis_results.csv'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    data_path = 'E:\\cit-22smcb0055\\SEM-V\\NLP\\project\\env\\nlp senti\\cleaned_data.csv'
    syntax_and_semantics_analysis(data_path)
