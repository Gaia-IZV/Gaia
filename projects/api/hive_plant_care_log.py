"""Async Hive logging for plant care APIs (queries + model responses)."""

import os
import threading
import uuid
from datetime import datetime

from dotenv import load_dotenv

_API_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(_API_ROOT, ".env"))

USING_EMR = os.environ.get("USING_EMR", "false").strip().lower() == "true"
EMR_IP = os.environ.get("EMR_IP")
_RESPONSE_MAX_LEN = int(os.environ.get("HIVE_RESPONSE_MAX_LEN", "4000"))


def _escape(value: str, max_len: int | None = None) -> str:
    s = str(value) if value is not None else ""
    if max_len is not None:
        s = s[:max_len]
    return (
        s.replace("\\", "\\\\")
        .replace("'", "''")
        .replace("|", " ")
        .replace(",", ";")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def get_hive_connection():
    from pyhive import hive

    conn = hive.Connection(host=EMR_IP, port=10000, database="gaia")
    print(f"[Hive] Connected to {EMR_IP}")
    return conn


def _log_plant_care_sync(
    username: str,
    user_query: str,
    source: str,
    k: int | None,
    model_id: str,
    response: str | None,
    fallback_reason: str | None = None,
) -> None:
    if not USING_EMR or not EMR_IP:
        return

    query_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_e = _escape(username)
    query_e = _escape(user_query)
    source_e = _escape(source)
    k_sql = str(int(k)) if k is not None else "NULL"

    conn = None
    try:
        conn = get_hive_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO gaia.plant_care_queries VALUES
            ('{query_id}', '{username_e}', '{query_e}', '{source_e}', {k_sql}, '{timestamp}')
            """
        )

        if response and str(response).strip():
            response_id = str(uuid.uuid4())
            model_e = _escape(model_id)
            response_e = _escape(response, max_len=_RESPONSE_MAX_LEN)
            if fallback_reason and str(fallback_reason).strip():
                fallback_e = _escape(fallback_reason)
                fallback_sql = f"'{fallback_e}'"
            else:
                fallback_sql = "NULL"
            cursor.execute(
                f"""
                INSERT INTO gaia.plant_care_responses VALUES
                ('{response_id}', '{query_id}', '{model_e}', '{response_e}', {fallback_sql}, '{timestamp}')
                """
            )

        conn.commit()
        print(f"[Hive] plant_care logged (source={source}, query_id={query_id})")
    except Exception as exc:
        print(f"[Hive] Failed to log plant_care: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def log_plant_care_interaction(
    username: str,
    user_query: str,
    source: str,
    k: int | None,
    model_id: str,
    response: str | None,
    fallback_reason: str | None = None,
) -> None:
    """Log query + optional response in a background thread."""
    t = threading.Thread(
        target=_log_plant_care_sync,
        args=(username, user_query, source, k, model_id, response, fallback_reason),
        daemon=True,
    )
    t.start()
