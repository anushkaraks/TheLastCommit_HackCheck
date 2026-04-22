from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    # Safe JSON parsing (won’t crash on bad input)
    data = request.get_json(silent=True) or {}

    # Required fields
    query = str(data.get("query", "")).lower().strip()
    assets = data.get("assets", [])  # accepted but not needed for this task

    # Extract integers (supports negatives)
    numbers = list(map(int, re.findall(r'-?\d+', query)))

    # Handle ONLY addition variants (be minimal & exact)
    if len(numbers) >= 2 and any(k in query for k in ["+", "add", "sum", "plus"]):
        result = numbers[0] + numbers[1]
        return jsonify({"output": f"The sum is {result}."})

    # Fallback (must also be exact & consistent)
    return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
