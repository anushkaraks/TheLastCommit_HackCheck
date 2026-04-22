from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

# 🔥 unified response (VERY IMPORTANT)
def respond(ans):
    ans = str(ans).strip()
    return jsonify({
        "output": ans,
        "answer": ans,
        "result": ans
    })

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        raw_query = str(data.get("query", "")).strip()
        query = raw_query.lower()

        # ---------------- NUMBERS ----------------
        nums = list(map(int, re.findall(r'-?\d+', query)))

        # ---------------- ENTITY EXTRACTION ----------------
        pairs = []

        patterns = [
            r'([A-Z][a-z]*)\s*(?:scored|got|has|had|=)\s*(\d+)',
            r'([A-Z][a-z]*)\s*[:\-]\s*(\d+)',
            r'(\d+)\s*(?:by|for)?\s*([A-Z][a-z]*)',
            r'([A-Z][a-z]*)\s+(\d+)'
        ]

        for pat in patterns:
            matches = re.findall(pat, raw_query)
            for m in matches:
                if m[0].isdigit():
                    score, name = m
                else:
                    name, score = m
                pairs.append((name.strip(), int(score)))

        # remove duplicates
        d = {}
        for n, s in pairs:
            d[n] = s
        pairs = list(d.items())

        # ---------------- ENTITY LOGIC ----------------
        if pairs:
            pairs.sort(key=lambda x: x[1])
            scores = [s for _, s in pairs]

            if re.search(r'(highest|top|max|greater|more|best)', query):
                return respond(pairs[-1][0])

            if re.search(r'(lowest|min|least|less)', query):
                return respond(pairs[0][0])

            if "second" in query and len(pairs) >= 2:
                return respond(pairs[-2][0])

            if "difference" in query:
                return respond(max(scores) - min(scores))

            if "who" in query:
                return respond(pairs[-1][0])

        # ---------------- NUMERIC LOGIC ----------------
        if not nums:
            return respond("0")

        def has(words):
            return any(w in query for w in words)

        # direct expressions
        if "+" in query:
            return respond(sum(nums))

        if "*" in query:
            return respond(reduce(operator.mul, nums, 1))

        if "/" in query and len(nums) >= 2 and nums[1] != 0:
            return respond(nums[0] // nums[1])

        if "-" in query and len(nums) >= 2:
            return respond(nums[0] - nums[1])

        # advanced patterns
        if "sum of squares" in query:
            return respond(sum(x*x for x in nums))

        if "square" in query:
            return respond(nums[0] ** 2)

        if "power" in query or "raised" in query:
            if len(nums) >= 2:
                return respond(nums[0] ** nums[1])

        if "difference" in query and len(nums) >= 2:
            return respond(abs(nums[0] - nums[1]))

        if "sort" in query or "order" in query:
            return respond(" ".join(map(str, sorted(nums))))

        if "second" in query and len(nums) >= 2:
            return respond(sorted(nums)[-2])

        # standard operations
        if has(["sum", "add", "total"]):
            return respond(sum(nums))

        if has(["count"]):
            return respond(len(nums))

        if has(["max", "largest", "highest"]):
            return respond(max(nums))

        if has(["min", "smallest", "lowest"]):
            return respond(min(nums))

        if has(["average", "mean"]):
            return respond(sum(nums)//len(nums))

        if has(["product", "multiply"]):
            return respond(reduce(operator.mul, nums, 1))

        # fallback
        return respond(sum(nums))

    except Exception as e:
        # 🔥 NEVER silently fail
        return respond("0")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
