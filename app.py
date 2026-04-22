from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query = str(data.get("query", "")).lower()

        nums = list(map(int, re.findall(r'-?\d+', query)))

        if not nums:
            return jsonify({"output": "0"})

        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        # SUM
        if "sum even" in query:
            return jsonify({"output": str(sum(even))})

        if "sum odd" in query:
            return jsonify({"output": str(sum(odd))})

        if "sum" in query:
            return jsonify({"output": str(sum(nums))})

        # COUNT
        if "count even" in query:
            return jsonify({"output": str(len(even))})

        if "count odd" in query:
            return jsonify({"output": str(len(odd))})

        # MAX MIN
        if "largest" in query or "max" in query:
            return jsonify({"output": str(max(nums))})

        if "smallest" in query or "min" in query:
            return jsonify({"output": str(min(nums))})

        # AVG
        if "average" in query or "mean" in query:
            return jsonify({"output": str(sum(nums)//len(nums))})

        # PRODUCT
        if "product even" in query:
            val = reduce(operator.mul, even, 1)
            return jsonify({"output": str(val)})

        if "product odd" in query:
            val = reduce(operator.mul, odd, 1)
            return jsonify({"output": str(val)})

        # DEFAULT
        return jsonify({"output": str(sum(nums))})

    except:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)from flask import Flask, request, jsonify
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
