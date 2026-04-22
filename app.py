from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

def respond(ans):
    return jsonify({"output": str(ans).strip()})

def safe_int(x):
    try:
        return int(x)
    except:
        return 0

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return respond("0")

        query = str(data.get("query", "")).strip()
        q = query.lower()

        # ---------- CLEAN TEXT ----------
        clean_q = re.sub(r'[^a-z0-9\s\-\+\*/\.]', ' ', q)

        # ---------- ENTITY EXTRACTION ----------
        # handles: "alice scored 80", "bob got 90", "john = 50"
        pairs = re.findall(r'([a-zA-Z]+)\s*(?:scored|got|has|=|is)?\s*(\d+)', query, re.I)
        name_score = {}

        for name, score in pairs:
            name_score[name.capitalize()] = safe_int(score)

        # ---------- NUMBER EXTRACTION ----------
        nums = list(map(int, re.findall(r'-?\d+', clean_q)))

        # ---------- KEYWORDS ----------
        def has(words):
            return any(w in clean_q for w in words)

        # ---------- ENTITY LOGIC ----------
        if name_score:
            if any(w in q for w in ["highest", "max", "top", "largest", "winner"]):
                return respond(max(name_score, key=name_score.get))

            if any(w in q for w in ["lowest", "min", "smallest", "least"]):
                return respond(min(name_score, key=name_score.get))

            if any(w in q for w in ["second", "2nd"]):
                sorted_names = sorted(name_score.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_names) >= 2:
                    return respond(sorted_names[1][0])

        # ---------- EDGE: NO NUMBERS ----------
        if not nums:
            if name_score:
                return respond(max(name_score, key=name_score.get))
            return respond("0")

        # ---------- FILTER ----------
        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]

        target = nums
        if "even" in clean_q:
            target = even if even else nums
        elif "odd" in clean_q:
            target = odd if odd else nums

        # ---------- SYMBOL OPS ----------
        if "+" in clean_q:
            return respond(sum(nums))

        if "*" in clean_q:
            return respond(reduce(operator.mul, nums, 1))

        if "/" in clean_q and len(nums) >= 2:
            try:
                result = nums[0]
                for n in nums[1:]:
                    if n == 0:
                        return respond("0")
                    result /= n
                return respond(int(result) if result == int(result) else result)
            except:
                return respond("0")

        if "-" in clean_q and len(nums) >= 2:
            result = nums[0]
            for n in nums[1:]:
                result -= n
            return respond(result)

        # ---------- WORD OPS ----------
        if has(["sum", "add", "total"]):
            return respond(sum(target))

        if has(["average", "mean"]):
            return respond(sum(target) // len(target))

        if has(["product", "multiply"]):
            return respond(reduce(operator.mul, target, 1))

        if has(["difference"]):
            if len(nums) >= 2:
                return respond(abs(nums[0] - nums[1]))

        if has(["square"]):
            return respond(nums[0] ** 2)

        if has(["count", "how many"]):
            return respond(len(target))

        if has(["max", "highest", "largest"]):
            return respond(max(target))

        if has(["min", "lowest", "smallest"]):
            return respond(min(target))

        if has(["sort", "arrange", "order"]):
            return respond(" ".join(map(str, sorted(target))))

        # ---------- SMART FALLBACKS ----------
        if name_score:
            return respond(max(name_score, key=name_score.get))

        return respond(max(nums))

    except:
        return respond("0")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
