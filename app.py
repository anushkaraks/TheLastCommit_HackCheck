from flask import Flask, request, jsonify
import re
from functools import reduce
import operator

app = Flask(__name__)

def respond(ans):
    return jsonify({"output": str(ans).strip()})

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    q = query.lower()

    # ---------------- ENTITY CASE ----------------
    # Example: Alice scored 80, Bob scored 90
    pairs = re.findall(r'([A-Z][a-z]*)\s*(?:scored|got|has|=)\s*(\d+)', query)

    if pairs:
        pairs = [(name, int(score)) for name, score in pairs]

        if "highest" in q or "max" in q or "top" in q:
            return respond(max(pairs, key=lambda x: x[1])[0])

        if "lowest" in q or "min" in q:
            return respond(min(pairs, key=lambda x: x[1])[0])

    # ---------------- NUMERIC CASE ----------------
    nums = list(map(int, re.findall(r'-?\d+', q)))

    if not nums:
        return respond("I cannot solve this.")

    # ADDITION
    if any(w in q for w in ["add", "sum", "plus", "+"]):
        return respond(f"The sum is {sum(nums)}.")

    # SUBTRACTION
    if any(w in q for w in ["subtract", "minus", "-"]):
        if "from" in q and len(nums) >= 2:
            result = nums[1] - nums[0]
        else:
            result = nums[0]
            for n in nums[1:]:
                result -= n
        return respond(f"The difference is {result}.")

    # MULTIPLICATION
    if any(w in q for w in ["multiply", "product", "*", "x"]):
        result = reduce(operator.mul, nums, 1)
        return respond(f"The product is {result}.")

    # DIVISION
    if any(w in q for w in ["divide", "/"]):
        try:
            result = nums[0]
            for n in nums[1:]:
                result /= n
            if result.is_integer():
                result = int(result)
            return respond(f"The quotient is {result}.")
        except:
            return respond("I cannot solve this.")

    return respond("I cannot solve this.")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
