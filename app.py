from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query_raw = str(data.get("query", "")).strip()
        query = query_raw.lower()

        # 🔹 LEVEL 5: WHO SCORED HIGHEST
        matches = re.findall(r'([A-Za-z]+)\s+scored\s+(\d+)', query_raw)
        if matches and "highest" in query:
            max_person = max(matches, key=lambda x: int(x[1]))
            return jsonify({"output": max_person[0]})

        # 🔹 LEVEL 4: SUM EVEN NUMBERS
        nums = list(map(int, re.findall(r'-?\d+', query)))
        if "sum even" in query:
            even_nums = [x for x in nums if x % 2 == 0]
            return jsonify({"output": str(sum(even_nums))})

        # 🔹 LEVEL 3: ODD / EVEN
        if "odd" in query and nums:
            return jsonify({"output": "YES" if nums[0] % 2 != 0 else "NO"})

        if "even" in query and nums:
            return jsonify({"output": "YES" if nums[0] % 2 == 0 else "NO"})

        # 🔹 LEVEL 2: DATE EXTRACTION
        date_match = re.search(r'\d{1,2} [A-Za-z]+ \d{4}', query_raw)
        if date_match:
            return jsonify({"output": date_match.group(0)})

        # 🔹 LEVEL 1: ADDITION
        if any(word in query for word in ["+", "add", "plus"]) and len(nums) >= 2:
            result = nums[0] + nums[1]
            return jsonify({"output": f"The sum is {result}."})

        # 🔹 FALLBACK
        return jsonify({"output": "I cannot solve this."})

    except:
        return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
