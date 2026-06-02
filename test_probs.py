import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

X_raw = []
y_raw = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        X_raw.append(pattern.lower())
        y_raw.append(intent['tag'])

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(X_raw)

model = LogisticRegression(random_state=42, max_iter=200)
model.fit(X, y_raw)

test_text = "see you later".lower()
X_test = vectorizer.transform([test_text])
probs = model.predict_proba(X_test)[0]
max_prob = np.max(probs)
pred = model.classes_[np.argmax(probs)]
print(f"Prediction for '{test_text}': {pred} with confidence {max_prob}")

model_c100 = LogisticRegression(random_state=42, max_iter=200, C=100)
model_c100.fit(X, y_raw)
probs_c100 = model_c100.predict_proba(X_test)[0]
max_prob_c100 = np.max(probs_c100)
print(f"Prediction (C=100) for '{test_text}': {pred} with confidence {max_prob_c100}")
