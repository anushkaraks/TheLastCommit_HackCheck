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

        clean_query = re.sub(r'[^a-z0-9\s\-\+\*/:]', ' ', query)

        nums = list(map(int, re.findall(r'-?\d+', clean_query)))

        # 🔥 ----------- ADVANCED ENTITY EXTRACTION -----------
        pairs = []

        # Alice scored 80 / Alice got 80 / Alice has 80
        pairs += re.findall(r'([a-z]+)\s*(?:scored|got|has|had|=)\s*(\d+)', query)

        # Alice: 80
        pairs += re.findall(r'([a-z]+)\s*[:\-]\s*(\d+)', query)

        # 80 by Alice
        pairs += re.findall(r'(\d+)\s*(?:by|for)?\s*([a-z]+)', query)

        # Normalize
        cleaned = []
        for p in pairs:
            if p[0].isdigit():
                score, name = p
            else:
                name, score = p
            cleaned.append((name.capitalize(), int(score)))

        # remove duplicates (keep latest)
        unique = {}
        for name, score in cleaned:
            unique[name] = score

        pairs = list(unique.items())
        # ----------------------------------------------------

        # 🔥 ----------- ENTITY REASONING -----------
        if pairs:
            scores = [s for _, s in pairs]
            max_score = max(scores)
            min_score = min(scores)

            # highest / top / more / greater
            if any(w in query for w in ["highest", "max", "top", "more", "greater", "best"]):
                winners = [n for n, s in pairs if s == max_score]
                return jsonify({"output": " ".join(winners)})

            # lowest / least
            if any(w in query for w in ["lowest", "min", "least", "less"]):
                losers = [n for n, s in pairs if s == min_score]
                return jsonify({"output": " ".join(losers)})

            # generic "who"
            if "who" in query:
                winners = [n for n, s in pairs if s == max_score]
                return jsonify({"output": " ".join(winners)})

        # ----------------------------------------------------

        if not nums:
            return jsonify({"output": "0"})

        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        def has(words):
            return any(w in query for w in words)

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
        POWER = ["power", "raised"]

        target = nums
        if has(EVEN):
            target = even
        elif has(ODD):
            target = odd

        if not target:
            return jsonify({"output": "0"})

        # 🔥 SYMBOL OPS
        if "+" in query:
            return jsonify({"output": str(sum(nums))})

        if "-" in query and len(nums) >= 2:
            return jsonify({"output": str(nums[0] - nums[1])})

        if "*" in query:
            return jsonify({"output": str(reduce(operator.mul, nums, 1))})

        if "/" in query and len(nums) >= 2 and nums[1] != 0:
            return jsonify({"output": str(nums[0] // nums[1])})

        # 🔥 POWER
        if has(POWER) and len(nums) >= 2:
            return jsonify({"output": str(nums[0] ** nums[1])})

        # 🔥 WORD OPS
        if has(SUM):
            return jsonify({"output": str(sum(target))})

        if has(COUNT):
            return jsonify({"output": str(len(target))})

        if has(MAX):
            return jsonify({"output": str(max(target))})

        if has(MIN):
            return jsonify({"output": str(min(target))})

        if has(AVG):
            return jsonify({"output": str(sum(target)//len(target))})

        if has(PRODUCT):
            return jsonify({"output": str(reduce(operator.mul, target, 1))})

        if has(DIFF) and len(nums) >= 2:
            return jsonify({"output": str(abs(nums[0] - nums[1]))})

        if has(SQUARE):
            return jsonify({"output": str(nums[0] ** 2)})

        if has(SORT):
            return jsonify({"output": " ".join(map(str, sorted(nums)))})

        # 🔥 SMART FALLBACK (IMPORTANT)
        # choose best possible guess instead of random
        if len(nums) == 1:
            return jsonify({"output": str(nums[0])})

        return jsonify({"output": str(sum(nums))})

    except:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
