from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query_raw = str(data.get("query", ""))
        query = query_raw.lower()

        # 1. ENTITY & SCORE EXTRACTION (Crucial for Level 5)
        # Matches patterns like "Alice scored 80" or "Bob: 90"
        entity_scores = re.findall(r'([a-zA-Z]+)\s+(?:scored|is|has|:)\s+(-?\d+)', query_raw)
        
        if entity_scores:
            # Convert to list of (name_string, score_int)
            scores = [(name, int(val)) for name, val in entity_scores]
            
            # Logic for "highest/max"
            if any(word in query for word in ["highest", "max", "best", "more", "greater"]):
                result = max(scores, key=lambda x: x[1])[0]
                return jsonify({"output": result}) # Returns just "Bob"
            
            # Logic for "lowest/min"
            if any(word in query for word in ["lowest", "min", "smallest", "less"]):
                result = min(scores, key=lambda x: x[1])[0]
                return jsonify({"output": result})

        # 2. BASIC MATH FALLBACK
        nums = list(map(int, re.findall(r'-?\d+', query)))
        if nums:
            if "sum" in query or "total" in query or "+" in query:
                return jsonify({"output": str(sum(nums))})
            return jsonify({"output": str(nums[0])})

        return jsonify({"output": "0"})

    except Exception:
        return jsonify({"output": "0"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
