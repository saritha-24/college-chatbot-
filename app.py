from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json
import difflib

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Load intents with UTF-8 encoding to avoid UnicodeDecodeError
with open('intents.json', encoding='utf-8') as f:
    intents_data = json.load(f)
    intents = intents_data['intents']

# DB setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ✅ Redirect root to login
@app.route("/")
def index():
    return redirect(url_for("login"))

# ✅ Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("chat"))  # ➜ redirect to chatbot
        else:
            flash("Invalid credentials.", "error")

    return render_template("login.html")

# ✅ Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")

    return render_template("register.html")

# ✅ Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# ✅ Chatbot Page
@app.route("/chat")
def chat():
    if "user" not in session:
        flash("You need to login first.", "error")
        return redirect(url_for("login"))
    return render_template("index.html")

# ✅ Chatbot Response — return all responses
@app.route("/get")
def chatbot_response():
    user_msg = request.args.get("msg", "").lower()

    best_match = None
    best_score = 0

    for intent in intents:
        for pattern in intent["patterns"]:
            score = difflib.SequenceMatcher(None, user_msg, pattern.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = intent

    if best_score > 0.6:
        return jsonify({
            "tag": best_match["tag"],
            "patterns": best_match["patterns"],
            "responses": best_match["responses"]  # ✅ return all responses
        })

    return jsonify({
        "reply": "Sorry, I didn't understand that. Please try again or contact support."
    })

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
