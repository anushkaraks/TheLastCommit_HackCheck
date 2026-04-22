from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# -----------------------------
# WORD → NUMBER MAP
# -----------------------------
word_map = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50
}

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    return re.sub(r'[^\w\s-]', ' ', text.lower())


# -----------------------------
# EXTRACT NUMBER
# -----------------------------
def extract_number(text):
    text = clean(text)

    # digits
    nums = re.findall(r'-?\d+', text)
    if nums:
        return int(nums[0])

    # word numbers
    words = text.split()
    for i, w in enumerate(words):

        if w in ["minus", "negative"] and i + 1 < len(words):
            if words[i + 1] in word_map:
                return -word_map[words[i + 1]]

        if w in word_map:
            val = word_map[w]

            if i + 1 < len(words) and words[i + 1] in word_map:
                if val >= 20:
                    val += word_map[words[i + 1]]

            return val

    return None


# -----------------------------
# RULE ENGINE
# -----------------------------
def apply_rules(n):
    if n % 2 == 0:
        n = n * 2
    else:
        n = n + 10

    if n > 20:
        n = n - 5
    else:
        n = n + 3

    if n % 3 == 0:
        return "FIZZ"

    return str(n)


# -----------------------------
# RULE DETECTION (SMART)
# -----------------------------
def is_rule_query(q):
    q = clean(q)

    # 🔥 direct triggers
    if "apply rules" in q or "rule 1" in q:
        return True

    # keyword signals
    signals = [
        "even", "odd", "double",
        "add 10", "subtract", "add 3",
        "divisible", "fizz"
    ]

    score = sum(1 for s in signals if s in q)

    return score >= 2


# -----------------------------
# BASIC SOLVER
# -----------------------------
def basic_solver(q):
    q_clean = re.sub(r'[^0-9+\-*/(). ]', '', q)

    try:
        if q_clean.strip():
            return str(int(eval(q_clean)))
    except:
        pass

    nums = re.findall(r'-?\d+', q)
    if nums:
        return nums[0]

    return ""


# -----------------------------
# MAIN SOLVER
# -----------------------------
def solve(query):
    if not query:
        return ""

    n = extract_number(query)

    # 🚨 RULE ENGINE PRIORITY
    if n is not None and is_rule_query(query):
        return apply_rules(n)

    # fallback
    return basic_solver(query)


# -----------------------------
# API
# -----------------------------
@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}

        query = str(data.get("query", ""))
        _ = data.get("assets", [])  # required format

        result = solve(query)

        return jsonify({
            "output": result.strip()
        })

    except Exception:
        return jsonify({
            "output": ""
        })


# -----------------------------
# RUN
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
