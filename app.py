from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

def normalize_output(ans):
    return str(ans).strip()

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
            r'([A-Z][a-z]*)\s+(\d+)'  # fallback
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

            # highest
            if re.search(r'(highest|top|max|greater|more|best)', query):
                max_val = max(scores)
                res = [n for n, s in pairs if s == max_val]
                return jsonify({"output": normalize_output(res[0])})

            # lowest
            if re.search(r'(lowest|min|least|less)', query):
                min_val = min(scores)
                res = [n for n, s in pairs if s == min_val]
                return jsonify({"output": normalize_output(res[0])})

            # second highest
            if "second" in query:
                if len(pairs) >= 2:
                    return jsonify({"output": normalize_output(pairs[-2][0])})

            # difference between top & bottom
            if "difference" in query:
                return jsonify({"output": normalize_output(max(scores) - min(scores))})

            # default who
            if "who" in query:
                return jsonify({"output": normalize_output(pairs[-1][0])})

        # ---------------- NUMERIC LOGIC ----------------
        if not nums:
            return jsonify({"output": "0"})

        def has(words):
            return any(w in query for w in words)

        # expressions
        if "+" in query:
            return jsonify({"output": normalize_output(sum(nums))})

        if "*" in query:
            return jsonify({"output": normalize_output(reduce(operator.mul, nums, 1))})

        if "/" in query and len(nums) >= 2 and nums[1] != 0:
            return jsonify({"output": normalize_output(nums[0] // nums[1])})

        if "-" in query and len(nums) >= 2:
            return jsonify({"output": normalize_output(nums[0] - nums[1])})

        # advanced patterns
        if "sum of squares" in query:
            return jsonify({"output": normalize_output(sum(x*x for x in nums))})

        if "square" in query:
            return jsonify({"output": normalize_output(nums[0]**2)})

        if "power" in query or "raised" in query:
            if len(nums) >= 2:
                return jsonify({"output": normalize_output(nums[0]**nums[1])})

        if "difference" in query and len(nums) >= 2:
            return jsonify({"output": normalize_output(abs(nums[0] - nums[1]))})

        if "sort" in query or "order" in query:
            return jsonify({"output": normalize_output(" ".join(map(str, sorted(nums))))})

        if "second" in query:
            if len(nums) >= 2:
                return jsonify({"output": normalize_output(sorted(nums)[-2])})

        # standard ops
        if has(["sum", "add", "total"]):
            return jsonify({"output": normalize_output(sum(nums))})

        if has(["count"]):
            return jsonify({"output": normalize_output(len(nums))})

        if has(["max", "largest", "highest"]):
            return jsonify({"output": normalize_output(max(nums))})

        if has(["min", "smallest", "lowest"]):
            return jsonify({"output": normalize_output(min(nums))})

        if has(["average", "mean"]):
            return jsonify({"output": normalize_output(sum(nums)//len(nums))})

        if has(["product", "multiply"]):
            return jsonify({"output": normalize_output(reduce(operator.mul, nums, 1))})

        # fallback
        return jsonify({"output": normalize_output(sum(nums))})

    except:
        return jsonify({"output": "0"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
