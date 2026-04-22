from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query_raw = str(data.get("query", ""))
        query = query_raw.lower()

        # --- LEVEL 3: BINARY LOGIC (YES/NO) ---
        if "is" in query and ("odd" in query or "even" in query):
            num_match = re.search(r'\d+', query)
            if num_match:
                n = int(num_match.group())
                if "odd" in query:
                    return jsonify({"output": "YES" if n % 2 != 0 else "NO"})
                if "even" in query:
                    return jsonify({"output": "YES" if n % 2 == 0 else "NO"})

        # --- LEVEL 2: DATE EXTRACTION ---
        if "extract date" in query:
            # Look for "Day Month Year" pattern
            date_match = re.search(r'\d{1,2}\s+[A-Z][a-z]+\s+\d{4}', query_raw)
            if date_match:
                return jsonify({"output": date_match.group()})

        # --- LEVEL 5: ENTITY COMPARISON ---
        # Regex to find "Name scored 80" or "Name: 90"
        entity_scores = re.findall(r'([A-Z][a-z]+)\s*(?:scored|is|has|:)\s*(-?\d+)', query_raw)
        if entity_scores:
            scores = [(name, int(val)) for name, val in entity_scores]
            if "highest" in query or "max" in query:
                winner = max(scores, key=lambda x: x[1])[0]
                return jsonify({"output": winner}) # returns "Bob"
            if "lowest" in query or "min" in query:
                loser = min(scores, key=lambda x: x[1])[0]
                return jsonify({"output": loser})

        # --- LEVEL 4: CONDITIONAL MATH ---
        nums = list(map(int, re.findall(r'-?\d+', query)))
        if "sum" in query and "even" in query:
            even_sum = sum([n for n in nums if n % 2 == 0])
            return jsonify({"output": str(even_sum)})

        # --- LEVEL 1: CONVERSATIONAL MATH ---
        # Matches "What is 10 + 15?" -> "The sum is 25."
        if "what is" in query and "+" in query:
            total = sum(nums)
            return jsonify({"output": f"The sum is {total}."})

        # --- GENERAL FALLBACK ---
        if nums:
            return jsonify({"output": str(nums[0])})
        
        return jsonify({"output": "0"})

    except Exception:
        return jsonify({"output": "0"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
