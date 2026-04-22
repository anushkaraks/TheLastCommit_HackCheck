from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").lower().strip()

    numbers = list(map(int, re.findall(r'-?\d+', query)))

    if any(word in query for word in ["+", "add", "sum", "plus"]) and len(numbers) >= 2:
        result = numbers[0] + numbers[1]   # ONLY FIRST TWO
        return jsonify({"output": f"The sum is {result}."})

    return jsonify({"output": "I cannot solve this."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
