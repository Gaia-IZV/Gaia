import json
import logging
import os
import threading
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from plant_semantic_search import search_plants

log = logging.getLogger(__name__)

_GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL = "llama-3.3-70b-versatile"

_API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_API_ROOT, ".env"))

USING_EMR = os.environ.get('USING_EMR', 'false').strip().lower() == 'true'
EMR_IP = os.environ.get('EMR_IP')

def get_hive_connection():
    from pyhive import hive
    conn = hive.Connection(
        host=EMR_IP,
        port=10000,
        database="gaia"
    )
    print(f"[Hive] Connected to {EMR_IP}")
    return conn


def _log_plant_care_query_sync(username, query, response_preview):
    if not USING_EMR or not EMR_IP:
        return
    conn = None
    try:
        conn = get_hive_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response_preview = (response_preview[:200] if response_preview else "").replace("'", "''").replace(",", ";")
        query_escaped = query.replace("'", "''").replace(",", ";")
        sql = f"""
            INSERT INTO gaia.plant_care_queries VALUES
            ('{uuid.uuid4()}', '{username}', '{query_escaped}', '{response_preview}', '{timestamp}')
        """
        cursor.execute(sql)
        conn.commit()
        print("[Hive] Plant care query logged")
    except Exception as e:
        print(f"[Hive] Failed to log plant care query: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def log_plant_care_query(username, query, response_preview):
    # Keep HTTP response fast even if Hive is slow/unavailable.
    t = threading.Thread(
        target=_log_plant_care_query_sync,
        args=(username, query, response_preview),
        daemon=True,
    )
    t.start()

app = Flask(__name__)
CORS(app)


def _groq_api_key() -> str | None:
    k = os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_KEY")
    if not k or not str(k).strip():
        return None
    return str(k).strip()


def humanize_plant_care(payload: dict) -> str | None:
    """Call Groq to turn search JSON into natural Spanish; None on skip or failure."""
    matches = payload.get("matches") or []
    if not matches:
        return (
            "No hay resultados en la base de datos para tu consulta. "
            "Prueba con otro nombre de planta o tema de cuidado."
        )

    key = _groq_api_key()
    if not key:
        return None

    system = (
        "Eres un asistente de jardinería para usuarios de hogar. "
        "Recibes JSON con la pregunta del usuario ('query') y candidatos en 'matches': "
        "cada uno tiene 'distance_l2' (menor = más parecido a la consulta) y 'plant' con "
        "name, scientific_name, sunlight, watering, pruning. "
        "Redacta una respuesta clara, amable y práctica en español. "
        "No inventes especies ni datos que no aparezcan en el JSON. "
        "Si hay varias plantas, resume o compara brevemente según la pregunta. "
        "No muestres el JSON ni listas técnicas crudas; solo texto natural."
    )
    user_content = json.dumps(payload, ensure_ascii=False)
    try:
        r = requests.post(
            _GROQ_CHAT_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            json={
                "model": _GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.55,
                "max_tokens": 1024,
            },
            timeout=90,
        )
        r.raise_for_status()
        data = r.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        msg = (choices[0].get("message") or {}).get("content")
        if not msg or not str(msg).strip():
            return None
        return str(msg).strip()
    except Exception:
        log.warning("Groq humanize failed", exc_info=True)
        return None


def _plant_payload(query: str, k_int: int) -> dict:
    raw = search_plants(query, k=k_int)
    raw["humanized"] = humanize_plant_care(raw)
    return raw


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/plant", methods=["POST"])
def plant_post():
    body = request.get_json(silent=True) or {}
    q = body.get("query") or body.get("q")
    username = body.get("username", "anonymous")
    if not q or not str(q).strip():
        return jsonify({'error': "Missing JSON field 'query' (or 'q')"}), 400
    k = body.get("k", 1)
    try:
        k_int = int(k)
    except (TypeError, ValueError):
        return jsonify({'error': "Invalid 'k'"}), 400
    result = _plant_payload(str(q).strip(), k_int)
    response_preview = result.get("humanized", "")[:200] if result.get("humanized") else ""
    log_plant_care_query(username, q, response_preview)
    return jsonify(result)


@app.route("/plant", methods=["GET"])
def plant_get():
    q = request.args.get("q") or request.args.get("query")
    username = request.args.get("username", "anonymous")
    if not q or not q.strip():
        return jsonify({'error': "Missing query parameter 'q' or 'query'"}), 400
    k_raw = request.args.get("k", "1")
    try:
        k_int = int(k_raw)
    except ValueError:
        return jsonify({'error': "Invalid 'k'"}), 400
    result = _plant_payload(q.strip(), k_int)
    response_preview = result.get("humanized", "")[:200] if result.get("humanized") else ""
    log_plant_care_query(username, q, response_preview)
    return jsonify(result)


def _debug_mode() -> bool:
    v = os.environ.get("FLASK_DEBUG", "true").strip().lower()
    return v in ("1", "true", "yes")


if __name__ == "__main__":
    port = int(os.environ.get("PLANT_CARE_PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=_debug_mode())
