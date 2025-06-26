from flask import Flask, render_template, request, redirect
import random, re, os

app = Flask(__name__)

MEMORY_FILE = "brain.txt"
CHATLOG_FILE = "chatlog.txt"
markov_chain = {}

def tokenize(text):
    return re.findall(r'\b\w+\b|[.!?]', text.lower())

def build_chain(words):
    for i in range(len(words) - 2):
        key = (words[i], words[i+1])
        next_word = words[i+2]
        markov_chain.setdefault(key, []).append(next_word)

def load_brain():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                words = tokenize(line.strip())
                if len(words) >= 1:
                    build_chain(words)

def save_to_brain(text):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

def append_to_chatlog(user_text, ai_text):
    with open(CHATLOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"You: {user_text}\nAI: {ai_text}\n")

def load_chatlog():
    if os.path.exists(CHATLOG_FILE):
        with open(CHATLOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def generate_response(seed=None, max_words=100):
    if not markov_chain:
        return "i would like a longer text, so i can learn"

    if seed:
        seed_words = tokenize(seed)
        if len(seed_words) >= 2:
            key = (seed_words[-2], seed_words[-1])
        else:
            key = random.choice(list(markov_chain.keys()))
    else:
        key = random.choice(list(markov_chain.keys()))

    if key not in markov_chain:
        key = random.choice(list(markov_chain.keys()))

    w1, w2 = key
    output = [w1, w2]

    for _ in range(max_words):
        next_words = markov_chain.get((w1, w2))
        if not next_words:
            break
        next_word = random.choice(next_words)
        output.append(next_word)
        w1, w2 = w2, next_word
        if next_word in ['.', '!', '?']:
            break

    return ' '.join(output).capitalize()

# Load the brain once
load_brain()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["message"].strip()
        if user_input:
            words = tokenize(user_input)
            if len(words) >= 1:
                build_chain(words)
                save_to_brain(user_input)
            response = generate_response(seed=user_input)
            append_to_chatlog(user_input, response)
        return redirect("/")  # avoid resubmission on refresh

    chatlog = load_chatlog()
    return render_template("index.html", chatlog=chatlog)

if __name__ == "__main__":
    app.run(debug=True)
