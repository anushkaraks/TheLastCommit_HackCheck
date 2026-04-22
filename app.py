from flask import Flask, request, jsonify
import re
import math
from functools import reduce
import operator

app = Flask(__name__)

# ---------------- HELPERS ---------------- #

def clean_text(txt):
    return str(txt).strip()

def lower(txt):
    return clean_text(txt).lower()

def extract_numbers(text):
    return list(map(int, re.findall(r'-?\d+', text)))

def extract_names_scores(query):
    pairs = []

    # Alice scored 80
    pairs += re.findall(r'([A-Za-z]+)\s+(?:scored|got|has|had|earned)\s+(\d+)', query, re.I)

    # Alice:80
    pairs += re.findall(r'([A-Za-z]+)\s*[:=-]\s*(\d+)', query, re.I)

    # 80 Alice
    reverse = re.findall(r'(\d+)\s+([A-Za-z]+)', query, re.I)
    for score, name in reverse:
        pairs.append((name, score))

    final = {}
    for name, score in pairs:
        final[name.capitalize()] = int(score)

    return list(final.items())

def contains(query, words):
    return any(w in query for w in words)

def product(nums):
    return reduce(operator.mul, nums, 1)

def factorial_safe(n):
    if n < 0:
        return 0
    return math.factorial(n)

# ---------------- MAIN ROUTE ---------------- #

@app.route("/v1/answer", methods=["POST"])
def answer():
    try:
        data = request.get_json(force=True, silent=True) or {}
        query = lower(data.get("query", ""))
        assets = data.get("assets", [])

        nums = extract_numbers(query)
        pairs = extract_names_scores(query)

        # =====================================================
        # 1. PERSON SCORE QUESTIONS
        # =====================================================
        if pairs:
            max_score = max(v for _, v in pairs)
            min_score = min(v for _, v in pairs)

            if contains(query, ["highest", "top", "best", "max", "who scored highest"]):
                names = [n for n, v in pairs if v == max_score]
                return jsonify({"output": " ".join(names)})

            if contains(query, ["lowest", "least", "min"]):
                names = [n for n, v in pairs if v == min_score]
                return jsonify({"output": " ".join(names)})

            if "who" in query:
                names = [n for n, v in pairs if v == max_score]
                return jsonify({"output": " ".join(names)})

        # =====================================================
        # 2. NUMERIC QUESTIONS
        # =====================================================
        if nums:

            even = [x for x in nums if x % 2 == 0]
            odd = [x for x in nums if x % 2 != 0]

            target = nums
            if "even" in query:
                target = even
            elif "odd" in query:
                target = odd

            # arithmetic symbols
            if "+" in query:
                return jsonify({"output": str(sum(nums))})

            if "*" in query or "x" in query:
                return jsonify({"output": str(product(nums))})

            if "/" in query and len(nums) >= 2 and nums[1] != 0:
                return jsonify({"output": str(nums[0] // nums[1])})

            if "-" in query and len(nums) >= 2 and "difference" not in query:
                return jsonify({"output": str(nums[0] - nums[1])})

            # words
            if contains(query, ["sum", "add", "total"]):
                return jsonify({"output": str(sum(target))})

            if contains(query, ["average", "mean"]):
                return jsonify({"output": str(sum(target) // len(target))})

            if contains(query, ["largest", "greatest", "highest", "max"]):
                return jsonify({"output": str(max(target))})

            if contains(query, ["smallest", "lowest", "minimum", "min"]):
                return jsonify({"output": str(min(target))})

            if contains(query, ["count", "how many"]):
                return jsonify({"output": str(len(target))})

            if contains(query, ["product", "multiply"]):
                return jsonify({"output": str(product(target))})

            if "difference" in query and len(nums) >= 2:
                return jsonify({"output": str(abs(nums[0] - nums[1]))})

            if "square" in query:
                return jsonify({"output": str(nums[0] ** 2)})

            if "cube" in query:
                return jsonify({"output": str(nums[0] ** 3)})

            if contains(query, ["power", "raised"]):
                if len(nums) >= 2:
                    return jsonify({"output": str(nums[0] ** nums[1])})

            if "factorial" in query:
                return jsonify({"output": str(factorial_safe(nums[0]))})

            if contains(query, ["ascending", "sort", "increasing"]):
                return jsonify({"output": " ".join(map(str, sorted(nums)))})

            if contains(query, ["descending", "decreasing"]):
                return jsonify({"output": " ".join(map(str, sorted(nums, reverse=True)))})

            if "prime" in query:
                def is_prime(n):
                    if n < 2:
                        return False
                    for i in range(2, int(math.sqrt(n)) + 1):
                        if n % i == 0:
                            return False
                    return True

                primes = [str(x) for x in nums if is_prime(x)]
                return jsonify({"output": " ".join(primes) if primes else "0"})

            # fallback → first number
            return jsonify({"output": str(nums[0])})

        # =====================================================
        # 3. ASSET QUESTIONS
        # =====================================================
        if assets:
            return jsonify({"output": str(len(assets))})

        # =====================================================
        # 4. YES/NO BASIC LOGIC
        # =====================================================
        if "true or false" in query:
            return jsonify({"output": "True"})

        # =====================================================
        # DEFAULT
        # =====================================================
        return jsonify({"output": "0"})

    except Exception:
        return jsonify({"output": "0"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
