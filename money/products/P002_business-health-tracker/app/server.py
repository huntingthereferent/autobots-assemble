import json
import mimetypes
import os
import pathlib
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")


def local_insight(data):
    profit = float(data.get("monthlyProfit", 0))
    units = int(data.get("unitsToBreakEven", 0))
    break_even = max(1, int(data.get("breakEvenUnits", 1)))
    margin = float(data.get("profitMargin", 0))

    if profit > 0:
        if margin < 0.10:
            return (
                "You are profitable, but the margin is thin. Test a small price "
                "increase or reduce one recurring cost before chasing more volume."
            )
        return (
            "You are above break-even. Protect the margin first, then test whether "
            "extra sales can be added without raising fixed costs."
        )

    if units <= max(3, round(break_even * 0.10)):
        noun = "unit" if units == 1 else "units"
        return (
            f"You are close to break-even. Focus on selling {units} more {noun} "
            "before making a larger change."
        )

    return (
        "You are below break-even. Start with the biggest lever: contribution per "
        "sale. Review price and product cost before adding more fixed expense."
    )


def openai_insight(data):
    if not OPENAI_API_KEY:
        return local_insight(data), "local"

    prompt = f"""
You are giving one plain-English business suggestion to a small business owner.
Do not use accounting jargon. Do not give tax, legal, investment, lending, or
personal financial advice. Use only the supplied operating numbers. Keep the
answer to one or two short sentences and recommend only one practical next move.

Numbers:
- Monthly revenue: {data.get("revenue")}
- Monthly profit/loss: {data.get("monthlyProfit")}
- Contribution per sale: {data.get("contributionPerUnit")}
- Break-even units: {data.get("breakEvenUnits")}
- Current monthly sales: {data.get("monthlySales")}
- Units still needed for break-even: {data.get("unitsToBreakEven")}
- Startup payback months: {data.get("paybackMonths")}
""".strip()

    body = json.dumps(
        {
            "model": OPENAI_MODEL,
            "input": prompt,
            "reasoning": {"effort": "none"},
            "text": {"verbosity": "low"},
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        text = payload.get("output_text")
        if not text:
            for item in payload.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text" and content.get("text"):
                        text = content["text"]
                        break
                if text:
                    break

        if text:
            return text.strip(), "openai"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        pass

    return local_insight(data), "local"


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        if self.path != "/api/insight":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            insight, source = openai_insight(data)
            self.send_json({"insight": insight, "source": source})
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid request"}, 400)

    def do_GET(self):
        requested = "index.html" if self.path in ("/", "") else self.path.lstrip("/")
        file_path = (ROOT / requested).resolve()

        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return

        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", (mime or "application/octet-stream") + ("; charset=utf-8" if (mime or "").startswith("text/") or file_path.suffix in {".js", ".mjs"} else ""))
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    print(f"Business Health Check running at http://{HOST}:{PORT}")
    print("AI insight:", "OpenAI enabled" if OPENAI_API_KEY else "local fallback (set OPENAI_API_KEY to enable OpenAI)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()