import json
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory, abort

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

# Mot de passe admin (à mettre dans systemd via env var)
ADMIN_PASSWORD = os.environ.get("COUNTDOWN_ADMIN_PASSWORD", "")

app = Flask(__name__, static_folder="static")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    # écriture atomique
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONFIG_PATH)


def is_valid_utc_iso(s: str) -> bool:
    # attend un ISO en UTC (Z ou +00:00)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.tzinfo is not None
    except Exception:
        return False


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/config")
def get_config():
    return jsonify(load_config())


@app.post("/api/config")
def set_config():
    if not ADMIN_PASSWORD:
        return jsonify({"error": "Admin password not set on server"}), 500

    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    target_utc = data.get("targetUtc")
    start_utc = data.get("startUtc")
    title = data.get("title")
    subtitle_prefix = data.get("subtitlePrefix")
    time_zone = data.get("timeZone")


    if not isinstance(start_utc, str) or not is_valid_utc_iso(start_utc):
        return jsonify({"error": "startUtc must be a valid ISO datetime with timezone, e.g. 2026-03-01T00:00:00Z"}), 400

    if not isinstance(target_utc, str) or not is_valid_utc_iso(target_utc):
        return jsonify({"error": "targetUtc must be a valid ISO datetime with timezone, e.g. 2026-03-20T17:00:00Z"}), 400

    cfg = load_config()
    cfg["targetUtc"] = target_utc

    if isinstance(time_zone, str) and time_zone:
        cfg["timeZone"] = time_zone
    if isinstance(title, str) and title:
        cfg["title"] = title
    if isinstance(subtitle_prefix, str) and subtitle_prefix:
        cfg["subtitlePrefix"] = subtitle_prefix

    cfg["startUtc"] = start_utc
    save_config(cfg)
    return jsonify({"ok": True, "config": cfg})


@app.get("/<path:path>")
def static_proxy(path):
    # sert les autres fichiers statiques (favicon, css etc si tu ajoutes)
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    # serveur dev intégré: OK pour LAN / test
    app.run(host="0.0.0.0", port=8000, threaded=True)
