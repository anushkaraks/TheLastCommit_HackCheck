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
# EXTRACT NUMBER (ROBUST)
# -----------------------------
def extract_number(text):
    text = text.lower()

    # digits first
    nums = re.findall(r'-?\d+', text)
    if nums:
        return int(nums[0])

    # word numbers
    words = text.split()
    for i, w in enumerate(words):
        if w in ["minus", "negative"] and i + 1 < len(words):
            nxt = words[i + 1]
            if nxt in word_map:
                return -word_map[nxt]

        if w in word_map:
            val = word_map[w]

            # handle "twenty one"
            if i + 1 < len(words) and words[i + 1] in word_map:
                if word_map[w] >= 20:
                    val += word_map[words[i + 1]]
            return val

    return None


# -----------------------------
# RULE ENGINE (STRICT)
# -----------------------------
def apply_rules(n):
    # Rule 1
    if n % 2 == 0:
        n = n * 2
    else:
        n = n + 10

    # Rule 2
    if n > 20:
        n = n - 5
    else:
        n = n + 3

    # Rule 3
    if n % 3 == 0:
        return "FIZZ"

    return str(n)


# -----------------------------
# SOLVER (KEY CHANGE)
# -----------------------------
def solve(query):
    if not query:
        return ""

    n = extract_number(query)

    if n is None:
        return ""

    # 🚨 ALWAYS APPLY RULES
    return apply_rules(n)


# -----------------------------
# API ROUTE
# -----------------------------
@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}

        query = str(data.get("query", ""))

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
