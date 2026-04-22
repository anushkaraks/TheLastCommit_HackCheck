from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip().lower()

    numbers = list(map(int, re.findall(r'-?\d+', query)))

    # 🔹 LEVEL 4: SUM EVEN NUMBERS
    if "even" in query and "sum" in query:
        even_nums = [n for n in numbers if n % 2 == 0]
        return jsonify({"output": str(sum(even_nums))})

    # 🔹 LEVEL 3: ODD / EVEN CHECK
    if "odd" in query and numbers:
        return jsonify({"output": "YES" if numbers[0] % 2 != 0 else "NO"})

    if "even" in query and numbers:
        return jsonify({"output": "YES" if numbers[0] % 2 == 0 else "NO"})

    # 🔹 LEVEL 2: DATE EXTRACTION
    date_match = re.search(r'\d{1,2} [A-Za-z]+ \d{4}', query)
    if date_match:
        return jsonify({"output": date_match.group(0)})

    # 🔹 LEVEL 1: ADDITION
    if any(word in query for word in ["+", "add", "sum", "plus"]) and len(numbers) >= 2:
        result = numbers[0] + numbers[1]
        return jsonify({"output": f"The sum is {result}."})

    # 🔹 FALLBACK
    return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
