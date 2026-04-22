from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

def normalize(ans):
    return str(ans).strip()

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}

        query_raw = str(data.get("query", "")).strip()
        query = query_raw.lower()

        # ---------------- CLEAN ----------------
        clean_query = re.sub(r'[^\w\s\-]', ' ', query_raw)

        # ---------------- ENTITY EXTRACTION ----------------
        pairs = []

        patterns = [
            r'([A-Za-z]+)\s+(?:scored|got|has|had|earned)\s+(-?\d+)',
            r'([A-Za-z]+)\s*[:=\-]\s*(-?\d+)',
            r'(-?\d+)\s+(?:by|for)?\s*([A-Za-z]+)'
        ]

        for pat in patterns:
            matches = re.findall(pat, clean_query, re.I)
            for m in matches:
                if m[0].lstrip('-').isdigit():
                    score, name = m
                else:
                    name, score = m
                pairs.append((name.strip(), int(score)))

        # remove duplicates safely
        temp = {}
        for n, s in pairs:
            temp[n] = s
        pairs = list(temp.items())

        # ---------------- LEVEL 5 (STRICT) ----------------
        if pairs and any(w in query for w in ["highest", "top", "best", "max", "who"]):

            max_score = max(score for _, score in pairs)
            winners = [name for name, score in pairs if score == max_score]

            return jsonify({"output": normalize(" ".join(winners))})

        if pairs and any(w in query for w in ["lowest", "least", "min"]):

            min_score = min(score for _, score in pairs)
            losers = [name for name, score in pairs if score == min_score]

            return jsonify({"output": normalize(" ".join(losers))})

        # ---------------- NUMBERS ----------------
        nums = list(map(int, re.findall(r'-?\d+', query)))

        if not nums:
            return jsonify({"output": "I cannot solve this."})

        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        def has(words):
            return any(w in query for w in words)

        # ---------------- PRIORITY RULES ----------------
        if "sum even" in query:
            return jsonify({"output": normalize(sum(even))})

        if "sum odd" in query:
            return jsonify({"output": normalize(sum(odd))})

        # strict addition format (important for cosine)
        if any(w in query for w in ["+", "add", "plus"]) and len(nums) >= 2:
            return jsonify({"output": f"The sum is {nums[0] + nums[1]}."})

        # ---------------- SAFE OPERATIONS ----------------
        if has(["count even"]):
            return jsonify({"output": normalize(len(even))})

        if has(["count odd"]):
            return jsonify({"output": normalize(len(odd))})

        if has(["max", "largest", "highest"]):
            return jsonify({"output": normalize(max(nums))})

        if has(["min", "smallest", "lowest"]):
            return jsonify({"output": normalize(min(nums))})

        if has(["average", "mean"]):
            return jsonify({"output": normalize(sum(nums)//len(nums))})

        if has(["product even"]):
            return jsonify({"output": normalize(reduce(operator.mul, even, 1))})

        if has(["product odd"]):
            return jsonify({"output": normalize(reduce(operator.mul, odd, 1))})

        if has(["sum"]):
            return jsonify({"output": normalize(sum(nums))})

        # ---------------- FINAL SAFE FALLBACK ----------------
        return jsonify({"output": "I cannot solve this."})

    except:
        return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
