from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json()
    query = data.get("query", "")

    # Extract numbers
    numbers = list(map(int, re.findall(r'\d+', query)))

    if "add" in query.lower() or "+" in query:
        result = sum(numbers)
        return f"The sum is {result}."

    # fallback
    return jsonify({"output": "I cannot solve this."})

if __name__ == '__main__':
    app.run(debug=True)
