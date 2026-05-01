import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def fmt_price(value, symbol):
    try:
        p = float(value)
        return f"{p:.2f}" if symbol == "XAUUSD" else f"{p:.5f}"
    except Exception:
        return str(value)


def build_message(data: dict) -> str:
    action = data.get("action", "")
    symbol = data.get("symbol", "Unknown")
    f = lambda v: fmt_price(v, symbol)

    if action == "BUY":
        return (
            f"🟢 *BUY Signal — {symbol}*\n"
            f"Type: `{data.get('type', 'Buy')}` | Score: `{data.get('score', '?')}`\n"
            f"────────────────\n"
            f"Entry      `{f(data.get('entry'))}`\n"
            f"Stop Loss  `{f(data.get('sl'))}`\n"
            f"Safe TP    `{f(data.get('tp1'))}`\n"
            f"TP 1       `{f(data.get('tp2'))}`\n"
            f"TP 2       `{f(data.get('tp3'))}`\n"
            f"R:R ≈ `{data.get('rr', '?')}`"
        )

    if action == "SELL":
        return (
            f"🔴 *SELL Signal — {symbol}*\n"
            f"Type: `{data.get('type', 'Sell')}` | Score: `{data.get('score', '?')}`\n"
            f"────────────────\n"
            f"Entry      `{f(data.get('entry'))}`\n"
            f"Stop Loss  `{f(data.get('sl'))}`\n"
            f"Safe TP    `{f(data.get('tp1'))}`\n"
            f"TP 1       `{f(data.get('tp2'))}`\n"
            f"TP 2       `{f(data.get('tp3'))}`\n"
            f"R:R ≈ `{data.get('rr', '?')}`"
        )

    if action == "SL_HIT":
        return (
            f"⚠️ *Stop Loss Hit — {symbol}*\n"
            f"Direction: `{data.get('direction', '?')}`\n"
            f"────────────────\n"
            f"Entry was  `{f(data.get('entry'))}`\n"
            f"Stop Loss  `{f(data.get('sl'))}`\n"
            f"❌ Trade closed at a loss"
        )

    return f"📊 FXSniper Alert\n```\n{json.dumps(data, indent=2)}\n```"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    text = build_message(data)
    resp = requests.post(
        TELEGRAM_URL,
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )

    if resp.status_code != 200:
        return jsonify({"error": "Telegram error", "detail": resp.text}), 500

    return jsonify({"ok": True}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"FXSniper webhook server running on port {port}")
    app.run(host="0.0.0.0", port=port)
