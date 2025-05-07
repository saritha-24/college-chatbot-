import json
import random
import pickle
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import nltk
from nltk.stem import WordNetLemmatizer

# Download necessary resources (only runs once)
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Load the inten
with open('intents.json') as file:
    data = json.load(file)

# Preprocessing
corpus = []
labels = []
for intent in data['intents']:
    for pattern in intent['patterns']:
        corpus.append(pattern.lower())
        labels.append(intent['tag'])

# Convert text to vectors
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(corpus)

# Train the model
model = MultinomialNB()
model.fit(X, labels)

# Save the model, vectorizer, and intents
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))
pickle.dump(data, open('intents.pkl', 'wb'))

print("✅ Model trained and saved as model.pkl")
