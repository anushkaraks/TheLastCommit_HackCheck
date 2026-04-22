from flask import Flask, request
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json()
    query = data.get("query", "").lower()

    # Extract numbers (handles negatives too)
    numbers = list(map(int, re.findall(r'-?\d+', query)))

    # Detect addition in multiple ways
    if any(word in query for word in ["+", "add", "sum", "plus"]) and len(numbers) >= 2:
        result = numbers[0] + numbers[1]
        return f"The sum is {result}."

    return "I cannot solve this."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
