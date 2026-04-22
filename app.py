from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query_raw = str(data.get("query", "")).strip()
        query = query_raw.lower()
        assets = data.get("assets", [])

        # ---------------------------
        # 🔥 LEVEL 5: ENTITY COMPARISON (ADDED)
        # ---------------------------
        clean_query = re.sub(r'[^\w\s\-]', ' ', query_raw)

        pairs = re.findall(
            r'([A-Za-z]+)\s+(?:scored|got|has|had)\s+(-?\d+)',
            clean_query
        )

        if pairs and any(w in query for w in ["highest", "max", "top", "best", "who"]):
            pairs = [(name, int(score)) for name, score in pairs]

            max_score = max(score for _, score in pairs)

            winners = [name for name, score in pairs if score == max_score]

            return jsonify({"output": " ".join(winners)})

        if pairs and any(w in query for w in ["lowest", "min", "least"]):
            pairs = [(name, int(score)) for name, score in pairs]

            min_score = min(score for _, score in pairs)

            losers = [name for name, score in pairs if score == min_score]

            return jsonify({"output": " ".join(losers)})

        # ---------------------------
        # 🔢 EXISTING LOGIC (UNCHANGED)
        # ---------------------------
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

        if has(query, DIFF) and len(nums) >= 2:
            return jsonify({"output": str(abs(nums[0] - nums[1]))})

        if has(query, SQUARE):
            return jsonify({"output": str(nums[0] ** 2)})

        if has(query, SORT):
            sorted_nums = sorted(nums)
            return jsonify({"output": " ".join(map(str, sorted_nums))})

        return jsonify({"output": str(sum(nums))})

    except:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
