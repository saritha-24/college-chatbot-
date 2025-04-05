from flask import Flask, request, jsonify, render_template
import random
import pickle

# Load saved files
model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
intents = pickle.load(open('intents.pkl', 'rb'))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["GET"])
def chatbot_response():
    user_input = request.args.get('msg')
    if not user_input:
        return jsonify({"reply": "Please type something..."})

    # Vectorize input and predict
    input_vector = vectorizer.transform([user_input.lower()])
    intent_tag = model.predict(input_vector)[0]

    # Find a response
    for intent in intents['intents']:
        if intent['tag'] == intent_tag:
            response = random.choice(intent['responses'])
            return jsonify({"reply": response})

    return jsonify({"reply": "I'm not sure how to answer that."})

if __name__ == "__main__":
    app.run(debug=True)
