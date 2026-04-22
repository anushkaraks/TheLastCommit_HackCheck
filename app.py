from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def process_query(query):
    # Extract number from query
    nums = re.findall(r'-?\d+', query)
    if not nums:
        return ""

    n = int(nums[0])

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
    else:
        return str(n)


@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}

        query = str(data.get("query", "")).strip()
        # assets are accepted but not needed for this logic
        # assets = data.get("assets", [])

        result = process_query(query)

        return jsonify({
            "output": result
        })

    except Exception as e:
        return jsonify({
            "output": ""
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
