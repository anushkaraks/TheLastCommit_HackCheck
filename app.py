from flask import Flask, request, jsonify
import re

app = Flask(__name__)


@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        # -----------------------------------------
        # REQUIRED INPUT FORMAT
        # {
        #   "query": "...",
        #   "assets": [...]
        # }
        # -----------------------------------------
        data = request.get_json(silent=True) or {}

        query = str(data.get("query", "")).strip()
        assets = data.get("assets", [])

        q = query.lower()

        # -----------------------------------------
        # LEVEL 5 : HIGHEST SCORE PERSON
        # Example:
        # Alice scored 80, Bob scored 90.
        # Who scored highest?
        # Output: Bob
        # -----------------------------------------

        # Extract name-number pairs
        pairs = re.findall(r'([A-Z][a-zA-Z]*)\s+scored\s+(\d+)', query)

        # fallback generic pair extraction
        if not pairs:
            pairs = re.findall(r'([A-Z][a-zA-Z]*)[^0-9]{0,15}(\d+)', query)

        if pairs:
            best_name = ""
            best_score = -1

            for name, score in pairs:
                score = int(score)

                if score > best_score:
                    best_score = score
                    best_name = name

            return jsonify({"output": best_name})

        # -----------------------------------------
        # EXTRA SMART FALLBACK
        # If names not capitalized
        # -----------------------------------------
        names = re.findall(r'[a-zA-Z]+', query)
        nums = list(map(int, re.findall(r'\d+', query)))

        if len(names) >= len(nums) and nums:
            idx = nums.index(max(nums))
            if idx < len(names):
                return jsonify({"output": names[idx].capitalize()})

        # -----------------------------------------
        # DEFAULT
        # -----------------------------------------
        return jsonify({"output": ""})

    except Exception:
        return jsonify({"output": ""})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
