import json
import random
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np

# Download required NLTK data securely if it hasn't been downloaded yet
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK data (punkt, wordnet)...")
        nltk.download('punkt')
        nltk.download('punkt_tab') # Needed for newer versions of nltk
        nltk.download('wordnet')
        nltk.download('omw-1.4')   # Often required by wordnet lemmatizer
        
download_nltk_data()

lemmatizer = WordNetLemmatizer()

MODEL_FILE = 'intent_model.joblib'
VECTORIZER_FILE = 'vectorizer.joblib'
INTENTS_FILE = 'intents.json'

def preprocess_text(text):
    """
    Tokenize and lemmatize the input text.
    Converts to lowercase, tokenizes into words, and lemmatizes each word.
    """
    tokens = word_tokenize(text.lower())
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(lemmatized)

def load_intents():
    """Load the training data from the intents JSON file."""
    with open(INTENTS_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def train_model():
    """
    Reads intents.json, vectorizes patterns using TF-IDF, trains a 
    Logistic Regression classifier, and saves the model artifacts to disk.
    """
    print("Training NLP Model...")
    intents = load_intents()
    
    X_raw = []
    y_raw = []
    
    # Extract patterns and their corresponding tags
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            X_raw.append(preprocess_text(pattern))
            y_raw.append(intent['tag'])
            
    # Convert text to numerical TF-IDF features
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(X_raw)
    
    # Train Logistic Regression classifier
    model = LogisticRegression(random_state=42, max_iter=200, C=100)
    model.fit(X, y_raw)
    
    # Save the model and vectorizer for inference
    joblib.dump(model, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)
    print("Model and vectorizer saved successfully to disk.")

def get_response(user_text):
    """
    Predicts the intent of the user text, checks confidence score, 
    and returns an appropriate response.
    """
    # Ensure models exist before inference
    if not os.path.exists(MODEL_FILE) or not os.path.exists(VECTORIZER_FILE):
        train_model()
        
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    intents = load_intents()
    
    # Preprocess and vectorize the input
    processed_text = preprocess_text(user_text)
    X_test = vectorizer.transform([processed_text])
    
    # Predict probabilities for all classes
    probabilities = model.predict_proba(X_test)[0]
    max_prob_index = np.argmax(probabilities)
    confidence = probabilities[max_prob_index]
    predicted_tag = model.classes_[max_prob_index]
    
    # Fallback if confidence is too low
    if confidence < 0.40:
        return {
            "response": "I'm sorry, I didn't quite understand that. Could you please rephrase?",
            "intent": "fallback",
            "confidence": float(confidence)
        }
        
    # Match the predicted tag to a random response
    for intent in intents['intents']:
        if intent['tag'] == predicted_tag:
            response = random.choice(intent['responses'])
            return {
                "response": response,
                "intent": predicted_tag,
                "confidence": float(confidence)
            }
            
    # Default error response
    return {
        "response": "I'm sorry, I encountered an error processing your request.",
        "intent": "error",
        "confidence": 0.0
    }

if __name__ == "__main__":
    # If run directly, just train the model
    train_model()
