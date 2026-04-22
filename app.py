from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).lower()

    numbers = list(map(int, re.findall(r'-?\d+', query)))

    if "sum even" in query:
        even_nums = [n for n in numbers if n % 2 == 0]
        return jsonify({"output": str(sum(even_nums))})

    return jsonify({"output": "I cannot solve this."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
