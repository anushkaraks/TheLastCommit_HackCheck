from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

def respond(ans):
    return jsonify({"output": str(ans).strip()})

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        raw = str(data.get("query", "")).strip()
        q = raw.lower()

        # -------- EXTRACT NUMBERS --------
        nums = list(map(int, re.findall(r'-?\d+', q)))

        # -------- LEVEL 3: YES/NO (ODD/EVEN) --------
        if "is" in q and ("odd" in q or "even" in q):
            if nums:
                n = nums[0]
                if "odd" in q:
                    return respond("YES" if n % 2 != 0 else "NO")
                if "even" in q:
                    return respond("YES" if n % 2 == 0 else "NO")

        # -------- LEVEL 2: DATE EXTRACTION --------
        if "date" in q:
            date_match = re.search(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', raw)
            if date_match:
                return respond(date_match.group())

        # -------- LEVEL 5: ENTITY COMPARISON --------
        patterns = [
            r'([A-Z][a-z]*)\s*(?:scored|got|has|=|is|:)\s*(-?\d+)',
            r'(-?\d+)\s*(?:by|for)?\s*([A-Z][a-z]*)'
        ]

        pairs = []
        for pat in patterns:
            matches = re.findall(pat, raw)
            for m in matches:
                if m[0].isdigit():
                    val, name = m
                else:
                    name, val = m
                pairs.append((name.strip(), int(val)))

        if pairs and any(w in q for w in ["highest", "max", "largest", "lowest", "min", "smallest"]):
            if any(w in q for w in ["highest", "max", "largest"]):
                return respond(max(pairs, key=lambda x: x[1])[0])
            if any(w in q for w in ["lowest", "min", "smallest"]):
                return respond(min(pairs, key=lambda x: x[1])[0])

        # -------- IF NO NUMBERS --------
        if not nums:
            return respond("0")

        # -------- FILTERS --------
        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        def has(words):
            return any(w in q for w in words)

        SUM = ["sum", "add", "total", "plus"]
        AVG = ["average", "mean"]
        MAX = ["max", "largest", "highest"]
        MIN = ["min", "smallest", "lowest"]
        COUNT = ["count", "how many"]
        PRODUCT = ["product", "multiply"]
        EVEN = ["even"]
        ODD = ["odd"]
        SORT = ["sort", "arrange", "order"]
        DIFF = ["difference", "subtract", "minus"]
        SQUARE = ["square"]

        target = nums
        if has(EVEN):
            target = even
        elif has(ODD):
            target = odd

        if not target:
            return respond("0")

        # -------- SYMBOL OPERATIONS --------
        if "+" in q:
            return respond(sum(nums))

        if "-" in q and len(nums) >= 2:
            return respond(nums[0] - nums[1])

        if "*" in q:
            return respond(reduce(operator.mul, nums, 1))

        if "/" in q and len(nums) >= 2 and nums[1] != 0:
            return respond(nums[0] / nums[1])

        # -------- WORD OPERATIONS --------
        if has(SUM):
            return respond(sum(target))

        if has(COUNT):
            return respond(len(target))

        if has(MAX):
            return respond(max(target))

        if has(MIN):
            return respond(min(target))

        if has(AVG):
            return respond(sum(target) // len(target))

        if has(PRODUCT):
            return respond(reduce(operator.mul, target, 1))

        if has(DIFF) and len(nums) >= 2:
            return respond(abs(nums[0] - nums[1]))

        if has(SQUARE):
            return respond(nums[0] ** 2)

        if has(SORT):
            return respond(" ".join(map(str, sorted(nums))))

        # -------- FINAL FALLBACK --------
        return respond(nums[0])

    except:
        return respond("0")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
