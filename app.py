from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip().lower()

    # LEVEL 3: ODD / EVEN
    if "odd" in query:
        numbers = list(map(int, re.findall(r'-?\d+', query)))
        if numbers:
            return jsonify({"output": "YES" if numbers[0] % 2 != 0 else "NO"})

    if "even" in query:
        numbers = list(map(int, re.findall(r'-?\d+', query)))
        if numbers:
            return jsonify({"output": "YES" if numbers[0] % 2 == 0 else "NO"})

    # LEVEL 2: DATE EXTRACTION
    date_match = re.search(r'\d{1,2} [A-Za-z]+ \d{4}', query)
    if date_match:
        return jsonify({"output": date_match.group(0)})

    # LEVEL 1: ADDITION
    numbers = list(map(int, re.findall(r'-?\d+', query)))
    if any(word in query for word in ["+", "add", "sum", "plus"]) and len(numbers) >= 2:
        result = numbers[0] + numbers[1]
        return jsonify({"output": f"The sum is {result}."})

    # FALLBACK
    return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
