import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from plant_semantic_search import search_plants

_API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_API_ROOT, ".env"))

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/plant", methods=["POST"])
def plant_post():
    body = request.get_json(silent=True) or {}
    q = body.get("query") or body.get("q")
    if not q or not str(q).strip():
        return jsonify({"error": "Missing JSON field 'query' (or 'q')"}), 400
    k = body.get("k", 1)
    try:
        k_int = int(k)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid 'k'"}), 400
    return jsonify(search_plants(str(q).strip(), k=k_int))


@app.route("/plant", methods=["GET"])
def plant_get():
    q = request.args.get("q") or request.args.get("query")
    if not q or not q.strip():
        return jsonify({"error": "Missing query parameter 'q' or 'query'"}), 400
    k_raw = request.args.get("k", "1")
    try:
        k_int = int(k_raw)
    except ValueError:
        return jsonify({"error": "Invalid 'k'"}), 400
    return jsonify(search_plants(q.strip(), k=k_int))


def _debug_mode() -> bool:
    v = os.environ.get("FLASK_DEBUG", "true").strip().lower()
    return v in ("1", "true", "yes")


if __name__ == "__main__":
    port = int(os.environ.get("PLANT_CARE_PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=_debug_mode())
