from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json(silent=True) or {}

        # Get query
        query_raw = str(data.get("query", "")).strip()
        query = query_raw.lower()

        # Clean punctuation (important for regex stability)
        clean_query = re.sub(r'[^\w\s\-]', ' ', query_raw)

        # ---------------------------
        # 🔥 LEVEL 5: ENTITY COMPARISON (ROBUST)
        # ---------------------------
        # Supports:
        # - multiple words in names (optional)
        # - multiple verbs
        # - negative numbers
        pairs = re.findall(
            r'([A-Za-z]+(?:\s[A-Za-z]+)?)\s+(?:scored|got|has|had|made)\s+(-?\d+)',
            clean_query
        )

        # Only trigger when clearly a comparison question
        if pairs and any(w in query for w in ["highest", "max", "top", "best", "who"]):

            # Convert scores to int
            pairs = [(name.strip(), int(score)) for name, score in pairs]

            # Find max score
            max_score = max(score for _, score in pairs)

            # Handle ties
            winners = [name for name, score in pairs if score == max_score]

            # EXACT FORMAT (critical)
            return jsonify({"output": " ".join(winners).strip()})

        # ---------------------------
        # ❌ SAFE FALLBACK
        # ---------------------------
        return jsonify({"output": "I cannot solve this."})

    except:
        return jsonify({"output": "I cannot solve this."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
