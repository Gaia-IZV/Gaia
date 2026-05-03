import os
import threading
import uuid
from datetime import datetime
from functools import lru_cache

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from huggingface_hub import HfApi
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

_API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_API_ROOT, ".env"))

app = Flask(__name__)
CORS(app)

USING_EMR = os.environ.get("USING_EMR", "false").strip().lower() == "true"
EMR_IP = os.environ.get("EMR_IP")


def _debug_mode() -> bool:
    value = os.environ.get("FLASK_DEBUG", "true").strip().lower()
    return value in ("1", "true", "yes")


def _hf_token() -> str:
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise ValueError("HF_TOKEN is missing in environment")
    return token


def get_hive_connection():
    from pyhive import hive

    conn = hive.Connection(
        host=EMR_IP,
        port=10000,
        database="gaia",
    )
    print(f"[Hive] Connected to {EMR_IP}")
    return conn


def _log_plant_care_query_sync(username: str, query: str, response_preview: str):
    if not USING_EMR or not EMR_IP:
        return
    conn = None
    try:
        conn = get_hive_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_preview = (response_preview[:200] if response_preview else "").replace("'", "''").replace(",", ";")
        query_escaped = query.replace("'", "''").replace(",", ";")
        sql = f"""
            INSERT INTO gaia.plant_care_queries VALUES
            ('{uuid.uuid4()}', '{username}', '{query_escaped}', '{response_preview}', '{timestamp}')
        """
        cursor.execute(sql)
        conn.commit()
        print("[Hive] plant_care_llm query logged")
    except Exception as exc:
        print(f"[Hive] Failed to log plant_care_llm query: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def log_plant_care_query(username: str, query: str, response_preview: str):
    # Keep HTTP response fast even if Hive is slow/unavailable.
    t = threading.Thread(
        target=_log_plant_care_query_sync,
        args=(username, query, response_preview),
        daemon=True,
    )
    t.start()


@lru_cache(maxsize=1)
def _hf_identity_and_repo() -> tuple[str, str]:
    token = _hf_token()
    username = HfApi().whoami(token=token)["name"]
    repo_name = os.environ.get("HF_REPO_NAME", "plantas-llm-finetuned").strip()
    if not repo_name:
        raise ValueError("HF_REPO_NAME cannot be empty")
    repo_id = f"{username}/{repo_name}"
    return username, repo_id


@lru_cache(maxsize=2)
def _hf_local_model(model_id: str) -> tuple[AutoTokenizer, AutoModelForCausalLM]:
    token = _hf_token()
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=token,
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        token=token,
        trust_remote_code=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model = model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    return tokenizer, model


def _fallback_model_id() -> str:
    return os.environ.get("HF_FALLBACK_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct").strip()


def _generate_with_fallback(prompt: str, max_new_tokens: int, temperature: float) -> tuple[str, str, str | None]:
    _, repo_id = _hf_identity_and_repo()
    candidates = [repo_id]
    fallback = _fallback_model_id()
    if fallback and fallback != repo_id:
        candidates.append(fallback)

    last_exc: Exception | None = None
    for idx, model_id in enumerate(candidates):
        try:
            tokenizer, model = _hf_local_model(model_id)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "### Respuesta:" in generated:
                generated = generated.split("### Respuesta:")[-1].strip()
            fallback_reason = None if idx == 0 else f"primary_model_failed: {type(last_exc).__name__ if last_exc else 'unknown'}"
            return model_id, generated.strip(), fallback_reason
        except Exception as exc:
            last_exc = exc
            continue

    raise RuntimeError(f"All candidate models failed. Last error: {type(last_exc).__name__}: {last_exc}")


def _prompt_from_request(body: dict) -> str:
    if body.get("prompt"):
        return str(body["prompt"]).strip()
    if body.get("planta"):
        planta = str(body["planta"]).strip()
        return (
            "### Instruccion:\n"
            f"Dame informacion sobre el cuidado de la planta {planta}.\n\n"
            "### Respuesta:"
        )
    return ""


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/whoami", methods=["GET"])
def whoami():
    try:
        username, repo_id = _hf_identity_and_repo()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"username": username, "repo_id": repo_id})


@app.route("/generate", methods=["POST"])
def generate_post():
    body = request.get_json(silent=True) or {}
    prompt = _prompt_from_request(body)
    username = str(body.get("username", "anonymous"))
    if not prompt:
        return jsonify({"error": "Missing JSON field 'prompt' or 'planta'"}), 400

    max_new_tokens = int(body.get("max_new_tokens", 200))
    temperature = float(body.get("temperature", 0.7))

    try:
        model_id, generated, fallback_reason = _generate_with_fallback(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
        log_plant_care_query(username, prompt, generated[:200])
        return jsonify(
            {
                "repo_id": model_id,
                "prompt": prompt,
                "response": generated,
                "fallback_reason": fallback_reason,
            }
        )
    except Exception as exc:
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 500


@app.route("/generate", methods=["GET"])
def generate_get():
    prompt = (request.args.get("prompt") or "").strip()
    username = (request.args.get("username") or "anonymous").strip()
    planta = (request.args.get("planta") or "").strip()
    if not prompt and planta:
        prompt = (
            "### Instruccion:\n"
            f"Dame informacion sobre el cuidado de la planta {planta}.\n\n"
            "### Respuesta:"
        )
    if not prompt:
        return jsonify({"error": "Missing query parameter 'prompt' or 'planta'"}), 400

    try:
        model_id, generated, fallback_reason = _generate_with_fallback(
            prompt=prompt,
            max_new_tokens=int(request.args.get("max_new_tokens", "200")),
            temperature=float(request.args.get("temperature", "0.7")),
        )
        log_plant_care_query(username, prompt, generated[:200])
        return jsonify(
            {
                "repo_id": model_id,
                "prompt": prompt,
                "response": generated,
                "fallback_reason": fallback_reason,
            }
        )
    except Exception as exc:
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PLANT_CARE_LLM_PORT", "5002"))
    app.run(host="0.0.0.0", port=port, debug=_debug_mode())
