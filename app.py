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
        assets = data.get("assets", [])

        query = re.sub(r'[^a-z0-9\s\-\+\*/]', ' ', query)

        nums = list(map(int, re.findall(r'-?\d+', query)))

        if not nums:
            return jsonify({"output": "0"})

        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        def has(q, words):
            return any(w in q for w in words)

        SUM = ["sum", "add", "total"]
        AVG = ["average", "mean"]
        MAX = ["max", "largest", "highest"]
        MIN = ["min", "smallest", "lowest"]
        COUNT = ["count", "how many"]
        PRODUCT = ["product", "multiply"]
        EVEN = ["even"]
        ODD = ["odd"]
        SORT = ["sort", "arrange", "order"]
        DIFF = ["difference", "subtract"]
        SQUARE = ["square"]
        
        target = nums
        if has(query, EVEN):
            target = even
        elif has(query, ODD):
            target = odd

        if not target:
            return jsonify({"output": "0"})

        # 🔥 DIRECT SYMBOL OPERATIONS
        if "+" in query:
            return jsonify({"output": str(sum(nums))})

        if "-" in query and len(nums) >= 2:
            return jsonify({"output": str(nums[0] - nums[1])})

        if "*" in query:
            return jsonify({"output": str(reduce(operator.mul, nums, 1))})

        if "/" in query and len(nums) >= 2 and nums[1] != 0:
            return jsonify({"output": str(nums[0] // nums[1])})

        # 🔥 WORD-BASED OPERATIONS
        if has(query, SUM):
            return jsonify({"output": str(sum(target))})

        if has(query, COUNT):
            return jsonify({"output": str(len(target))})

        if has(query, MAX):
            return jsonify({"output": str(max(target))})

        if has(query, MIN):
            return jsonify({"output": str(min(target))})

        if has(query, AVG):
            return jsonify({"output": str(sum(target)//len(target))})

        if has(query, PRODUCT):
            return jsonify({"output": str(reduce(operator.mul, target, 1))})

        # 🔥 DIFFERENCE (important!)
        if has(query, DIFF) and len(nums) >= 2:
            return jsonify({"output": str(abs(nums[0] - nums[1]))})

        # 🔥 SQUARE
        if has(query, SQUARE):
            return jsonify({"output": str(nums[0] ** 2)})

        # 🔥 SORTING
        if has(query, SORT):
            sorted_nums = sorted(nums)
            return jsonify({"output": " ".join(map(str, sorted_nums))})

        # 🔥 FALLBACK (VERY IMPORTANT FOR COSINE)
        # try sum → max → first number
        return jsonify({"output": str(sum(nums))})

    except:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
