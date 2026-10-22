import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from pathlib import Path

import joblib
import requests
from dotenv import load_dotenv

# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# Qwen general chat (fallback for non-definition/formula intents)
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
QWEN_MODEL = "qwen2.5:1.5b"

CHAT_SYSTEM_PROMPT = (
    "You are CUBE, a helpful educational AI assistant. "
    "Only respond to what the user actually says. "
    "Keep replies concise and relevant."
)

CHAT_OPTIONS = {
    "temperature": 0.6,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_predict": 150,
}


def stream_chat_reply(query: str):
    """Stream token chunks from Qwen via Ollama."""

    with requests.post(
        OLLAMA_URL,
        json={
            "model": QWEN_MODEL,
            "messages": [
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            "stream": True,
            "options": CHAT_OPTIONS,
        },
        stream=True,
        timeout=60,
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            try:
                chunk = json.loads(line.decode("utf-8"))

            except Exception:
                continue

            piece = chunk.get("message", {}).get("content")

            if piece:
                yield piece

            if chunk.get("done"):
                break


# ============================================================
# Model files
# ============================================================

BASE = Path(__file__).parent


try:
    clf = final_clf
    vectorizer = final_vectorizer
    print("Using model already in memory.")

except NameError:
    clf = joblib.load(BASE / "logreg_model.joblib")
    vectorizer = joblib.load(BASE / "tfidf_vectorizer.joblib")
    print("Loaded model from disk.")


# ============================================================
# Definition pipeline
# ============================================================

try:
    from topic_extractor import match_topic
    from definition_lookup import get_definition

    print("Definition pipeline loaded.")

except ImportError as e:
    raise SystemExit(
        f"Could not import definition pipeline: {e}"
    )


# ============================================================
# Formula pipeline
# ============================================================

try:
    from formula_extractor import match_formula
    from formula_lookup import get_formula

    print("Formula pipeline loaded.")

except ImportError as e:
    raise SystemExit(
        f"Could not import formula pipeline: {e}"
    )


print(f"Classes: {list(clf.classes_)}")


# ============================================================
# HTTP Handler
# ============================================================

class Handler(BaseHTTPRequestHandler):

    # --------------------------------------------------------
    # JSON response
    # --------------------------------------------------------

    def _send_json(
        self,
        code: int,
        payload: dict
    ):

        body = json.dumps(payload).encode("utf-8")

        self.send_response(code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

        self.wfile.write(body)


    # --------------------------------------------------------
    # Streaming response helpers
    # --------------------------------------------------------

    def _send_stream_start(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/x-ndjson; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        # Prevent reverse proxies from buffering the stream
        self.send_header(
            "X-Accel-Buffering",
            "no"
        )

        self.end_headers()


    def _write_event(self, payload: dict):

        self.wfile.write(
            (json.dumps(payload) + "\n").encode("utf-8")
        )

        self.wfile.flush()


    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()


    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        path = urlparse(self.path).path

        # ----------------------------------------------------
        # Health check
        # ----------------------------------------------------

        if path == "/health":

            self._send_json(
                200,
                {
                    "ok": True,
                    "status": "alive"
                }
            )

            return

        # ----------------------------------------------------
        # Not found
        # ----------------------------------------------------

        self._send_json(
            404,
            {
                "ok": False,
                "error": "Not found."
            }
        )


    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def do_POST(self):

        path = urlparse(self.path).path

        # ----------------------------------------------------
        # Read request body
        # ----------------------------------------------------

        length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        raw = (
            self.rfile.read(length)
            if length
            else b"{}"
        )

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:

            payload = json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            self._send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON."
                }
            )

            return


        # ====================================================
        # /query  (streaming)
        # ====================================================

        if path == "/query":

            query = (
                payload.get("query") or ""
            ).strip()

            if not query:

                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Empty query."
                    }
                )

                return

            # ----------------------------------------------------
            # Classifier still runs for logging/visibility only —
            # NOT used for routing right now while the classifier
            # is being rebuilt. Every query streams straight from
            # Qwen below.
            # ----------------------------------------------------

            vec = vectorizer.transform([query])

            pred = clf.predict(vec)[0]

            print(
                f"[{query!r}] -> {pred} "
                f"(routing: qwen, classifier bypassed)"
            )

            # ----------------------------------------------------
            # Stream tokens back to the client as they arrive
            # ----------------------------------------------------

            try:

                self._send_stream_start()

                for piece in stream_chat_reply(query):

                    self._write_event(
                        {
                            "type": "token",
                            "text": piece
                        }
                    )

                self._write_event({"type": "done"})

            except Exception as e:

                print("[chat error]", e)

                try:

                    self._write_event(
                        {
                            "type": "error",
                            "error": str(e)
                        }
                    )

                except Exception:
                    pass

            return


        # ====================================================
        # /formula
        # ====================================================

        if path == "/formula":

            query = payload.get(
                "query",
                ""
            ).strip()

            if not query:

                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": "No query provided."
                    }
                )

                return

            try:

                result = match_formula(query)

                resp = {
                    "ok": True,
                    "query": query,
                    "extracted": result["extracted"],
                    "matched": result["matched"],
                    "score": float(result["score"]),
                    "method": result["method"],
                }

                if result["matched"] is None:

                    resp["ok"] = False

                    resp["error"] = (
                        "No matching formula found "
                        "for this topic."
                    )

                else:

                    entry = get_formula(result["matched"])

                    if entry is None:

                        resp["ok"] = False

                        resp["error"] = (
                            f"Formula key "
                            f"'{result['matched']}' "
                            "has no entry on file."
                        )

                    else:

                        resp["subject"] = entry["subject"]
                        resp["topic"] = entry["topic"]
                        resp["key"] = entry["key"]
                        resp["formula"] = entry["formula"]

            except Exception as e:

                print("[formula error]", e)

                resp = {
                    "ok": False,
                    "error": str(e)
                }

            self._send_json(
                200,
                resp
            )

            return


        # ====================================================
        # /definition
        # ====================================================

        if path == "/definition":

            query = payload.get(
                "query",
                ""
            ).strip()

            if not query:

                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": "No query provided."
                    }
                )

                return

            try:

                result = match_topic(query)

                resp = {
                    "ok": True,
                    "query": query,
                    "extracted": result["extracted"],
                    "matched": result["matched"],
                    "score": float(result["score"]),
                    "method": result["method"],
                }

                if result["matched"] is None:

                    resp["ok"] = False

                    resp["error"] = (
                        "No matching term found "
                        "for this topic."
                    )

                else:

                    entry = get_definition(result["matched"])

                    if entry is None:

                        resp["ok"] = False

                        resp["error"] = (
                            f"Term '{result['matched']}' "
                            "has no definition on file."
                        )

                    else:

                        resp["subject"] = entry["subject"]
                        resp["topic"] = entry["topic"]
                        resp["term"] = entry["term"]
                        resp["definition"] = entry["definition"]

            except Exception as e:

                print("[definition error]", e)

                resp = {
                    "ok": False,
                    "error": str(e)
                }

            self._send_json(
                200,
                resp
            )

            return


        # ====================================================
        # Unknown endpoint
        # ====================================================

        self._send_json(
            404,
            {
                "ok": False,
                "error": "Not found."
            }
        )


    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    def log_message(
        self,
        fmt,
        *args
    ):

        print(
            f"[http] "
            f"{self.address_string()} "
            f"- {fmt % args}"
        )


# ============================================================
# Start server
# ============================================================

if __name__ == "__main__":

    # "0.0.0.0" binds to every available network interface, so this
    # keeps working even if your LAN/hotspot IP changes. Use
    # "127.0.0.1" instead if you only need local-machine access.
    host = "0.0.0.0"
    port = 8004

    server = HTTPServer(
        (host, port),
        Handler
    )

    print(
        f"Serving CUBE API on "
        f"http://{host}:{port}"
    )

    print(
        "Endpoints:"
    )

    print(
        "  GET  /health"
    )

    print(
        "  POST /query        (streaming NDJSON)"
    )

    print(
        "  POST /definition"
    )

    print(
        "  POST /formula"
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nShutting down."
        )

        server.server_close()