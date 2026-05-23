import os
import sys
from functools import lru_cache

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from huggingface_hub import HfApi, hf_hub_download
from peft import AutoPeftModelForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

_APP_DIR = os.path.abspath(os.path.dirname(__file__))
_API_ROOT = os.path.abspath(os.path.join(_APP_DIR, ".."))
for _p in (_APP_DIR, _API_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
load_dotenv(os.path.join(_API_ROOT, ".env"))

from hive_plant_care_log import log_plant_care_interaction  # noqa: E402

app = Flask(__name__)
CORS(app)


def _debug_mode() -> bool:
    value = os.environ.get("FLASK_DEBUG", "true").strip().lower()
    return value in ("1", "true", "yes")


def _hf_token() -> str:
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise ValueError("HF_TOKEN is missing in environment")
    return token


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
def _hf_local_model(model_id: str) -> tuple[AutoTokenizer, AutoModelForCausalLM | AutoPeftModelForCausalLM]:
    token = _hf_token()
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=token,
        trust_remote_code=True,
    )
    use_device_map = os.environ.get("HF_USE_DEVICE_MAP", "true").strip().lower() in ("1", "true", "yes")
    torch_dtype = torch.bfloat16

    is_adapter_repo = False
    try:
        hf_hub_download(repo_id=model_id, filename="adapter_config.json", token=token)
        is_adapter_repo = True
    except Exception:
        is_adapter_repo = False

    if is_adapter_repo:
        if use_device_map:
            model = AutoPeftModelForCausalLM.from_pretrained(
                model_id,
                token=token,
                trust_remote_code=True,
                device_map="auto",
                torch_dtype=torch_dtype,
            )
        else:
            model = AutoPeftModelForCausalLM.from_pretrained(
                model_id,
                token=token,
                trust_remote_code=True,
                torch_dtype=torch_dtype,
            )
            model = model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        return tokenizer, model

    if use_device_map:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=token,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch_dtype,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=token,
            trust_remote_code=True,
            torch_dtype=torch_dtype,
        )
        model = model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    return tokenizer, model


def _fallback_model_id() -> str:
    # Optional: only used if explicitly set in the environment.
    return os.environ.get("HF_FALLBACK_MODEL_ID", "").strip()


def _generate_with_fallback(prompt: str, max_new_tokens: int, temperature: float) -> tuple[str, str, str | None]:
    _, repo_id = _hf_identity_and_repo()
    candidates = [repo_id]
    fallback = _fallback_model_id()
    if fallback and fallback != repo_id:
        candidates.append(fallback)

    last_exc: Exception | None = None
    primary_exc: Exception | None = None
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
            if idx == 0:
                return model_id, generated.strip(), None
            return model_id, generated.strip(), f"primary_model_failed: {type(primary_exc).__name__}: {primary_exc}"
        except Exception as exc:
            last_exc = exc
            if idx == 0:
                primary_exc = exc
            continue

    raise RuntimeError(f"All candidate models failed. Last error: {type(last_exc).__name__}: {last_exc}")


def _generate_primary(prompt: str, max_new_tokens: int, temperature: float) -> tuple[str, str]:
    _, repo_id = _hf_identity_and_repo()
    tokenizer, model = _hf_local_model(repo_id)
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
    return repo_id, generated.strip()


def _prompt_from_request(body: dict) -> str:
    if body.get("prompt"):
        return str(body["prompt"]).strip()
    if body.get("planta"):
        planta = str(body["planta"]).strip()
        return (
            "### Instrucción:\n"
            f"Dame información sobre el cuidado de la planta {planta}.\n\n"
            "### Respuesta:"
        )
    return ""


def _user_query_from_body(body: dict) -> str:
    if body.get("planta"):
        return str(body["planta"]).strip()
    if body.get("prompt"):
        return str(body["prompt"]).strip()
    return ""


def _user_query_from_args(prompt: str, planta: str) -> str:
    if planta:
        return planta.strip()
    return prompt.strip()


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
        fallback = _fallback_model_id()
        if fallback:
            model_id, generated, fallback_reason = _generate_with_fallback(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
            )
        else:
            model_id, generated = _generate_primary(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
            )
            fallback_reason = None
        log_plant_care_interaction(
            username=username,
            user_query=_user_query_from_body(body),
            source="llm",
            k=None,
            model_id=model_id,
            response=generated,
            fallback_reason=fallback_reason,
        )
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
            "### Instrucción:\n"
            f"Dame información sobre el cuidado de la planta {planta}.\n\n"
            "### Respuesta:"
        )
    if not prompt:
        return jsonify({"error": "Missing query parameter 'prompt' or 'planta'"}), 400

    try:
        fallback = _fallback_model_id()
        if fallback:
            model_id, generated, fallback_reason = _generate_with_fallback(
                prompt=prompt,
                max_new_tokens=int(request.args.get("max_new_tokens", "200")),
                temperature=float(request.args.get("temperature", "0.7")),
            )
        else:
            model_id, generated = _generate_primary(
                prompt=prompt,
                max_new_tokens=int(request.args.get("max_new_tokens", "200")),
                temperature=float(request.args.get("temperature", "0.7")),
            )
            fallback_reason = None
        log_plant_care_interaction(
            username=username,
            user_query=_user_query_from_args(prompt, planta),
            source="llm",
            k=None,
            model_id=model_id,
            response=generated,
            fallback_reason=fallback_reason,
        )
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
