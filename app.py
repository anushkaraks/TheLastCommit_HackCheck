from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)


@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        # --------------------------------------------
        # ACCEPT POST JSON FORMAT
        # {
        #   "query": "...",
        #   "assets": [...]
        # }
        # --------------------------------------------
        data = request.get_json(silent=True) or {}

        query = str(data.get("query", "")).strip().lower()
        assets = data.get("assets", [])   # accepted as per requirement

        # Extract all integers
        nums = list(map(int, re.findall(r'-?\d+', query)))

        if not nums:
            return jsonify({"output": "0"})

        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        # ==================================================
        # LEVEL 4 UNIVERSAL NUMBER OPERATIONS
        # ==================================================

        # SUM EVEN
        if "sum even" in query:
            return jsonify({"output": str(sum(even))})

        # SUM ODD
        if "sum odd" in query:
            return jsonify({"output": str(sum(odd))})

        # SUM ALL
        if "sum" in query or "total" in query:
            return jsonify({"output": str(sum(nums))})

        # COUNT EVEN
        if "count even" in query:
            return jsonify({"output": str(len(even))})

        # COUNT ODD
        if "count odd" in query:
            return jsonify({"output": str(len(odd))})

        # COUNT ALL
        if "count" in query:
            return jsonify({"output": str(len(nums))})

        # MAX
        if any(word in query for word in ["largest", "maximum", "max", "greatest"]):
            return jsonify({"output": str(max(nums))})

        # MIN
        if any(word in query for word in ["smallest", "minimum", "min", "least"]):
            return jsonify({"output": str(min(nums))})

        # AVERAGE
        if any(word in query for word in ["average", "mean"]):
            return jsonify({"output": str(sum(nums) // len(nums))})

        # PRODUCT EVEN
        if "product even" in query:
            val = reduce(operator.mul, even, 1)
            return jsonify({"output": str(val)})

        # PRODUCT ODD
        if "product odd" in query:
            val = reduce(operator.mul, odd, 1)
            return jsonify({"output": str(val)})

        # PRODUCT ALL
        if any(word in query for word in ["product", "multiply"]):
            val = reduce(operator.mul, nums, 1)
            return jsonify({"output": str(val)})

        # SORT ASC
        if "ascending" in query or "sort" in query:
            return jsonify({"output": ",".join(map(str, sorted(nums)))})

        # SORT DESC
        if "descending" in query:
            return jsonify({"output": ",".join(map(str, sorted(nums, reverse=True)))})

        # SECOND LARGEST
        if "second largest" in query:
            unique = sorted(set(nums), reverse=True)
            return jsonify({"output": str(unique[1] if len(unique) > 1 else unique[0])})

        # SECOND SMALLEST
        if "second smallest" in query:
            unique = sorted(set(nums))
            return jsonify({"output": str(unique[1] if len(unique) > 1 else unique[0])})

        # DEFAULT SAFE RESPONSE
        return jsonify({"output": str(sum(nums))})

    except Exception:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
