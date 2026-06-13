#!/usr/bin/env python3
from __future__ import annotations

import http.server
import json
import io
import re
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse
from pathlib import Path

from rembg import remove, new_session
from PIL import Image
from onnxruntime import SessionOptions


HOST: str = "0.0.0.0"
PORT: int = 8080

opts = SessionOptions()
opts.intra_op_num_threads = 1
session = new_session(
    model_name="isnet-anime",
    session_options=opts,
)


HandlerFn = Callable[["Handler"], None]


@dataclass
class Router:
    _routes: dict[str, dict[str, HandlerFn]] = field(default_factory=lambda: {"GET": {}, "POST": {}})

    def route(self, method: str, path: str) -> Callable[[HandlerFn], HandlerFn]:
        def decorator(fn: HandlerFn) -> HandlerFn:
            self._routes.setdefault(method, {})[path] = fn
            return fn
        return decorator

    def dispatch(self, handler: "Handler", method: str, path: str) -> None:
        fn = self._routes.get(method, {}).get(path)
        if fn:
            return fn(handler)
        handler._json(404, {"error": "Ruta no encontrada"})


router = Router()


@router.route("GET", "/")
def index(handler: "Handler") -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(Path("server.html").read_bytes())


@router.route("GET", "/api/models")
def models(handler: "Handler") -> None:
    handler._json(200, [
        "u2net", "u2netp", "u2net_human_seg", "u2net_cloth_seg",
        "silueta", "isnet-general-use", "isnet-anime", "sam",
    ])


def _parse_multipart(body: bytes, boundary: str) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    parts = body.split(f"--{boundary}".encode())
    for part in parts:
        if b"Content-Disposition" not in part:
            continue
        header, _, payload = part.partition(b"\r\n\r\n")
        payload = payload.rstrip(b"\r\n--")
        name_match = re.search(rb'name="([^"]+)"', header)
        if name_match:
            result[name_match.group(1).decode()] = payload
    return result


@router.route("POST", "/api/remove-bg")
def remove_bg(handler: "Handler") -> None:
    ctype = handler.headers.get("Content-Type", "")
    match = re.match(r"^multipart/form-data;\s*boundary=(.+)$", ctype)
    if not match:
        handler._json(400, {"error": "Se requiere multipart/form-data"})
        return

    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length)
    fields = _parse_multipart(body, match.group(1))
    img_data = fields.get("image")

    if not img_data:
        handler._json(400, {"error": "Campo 'image' requerido"})
        return

    try:
        input_image = Image.open(io.BytesIO(img_data))
        output = remove(input_image, session=session)
        buf = io.BytesIO()
        output.save(buf, format="PNG")
        buf.seek(0)

        handler.send_response(200)
        handler.send_header("Content-Type", "image/png")
        handler.send_header("Content-Disposition", "attachment; filename=sin_fondo.png")
        handler.end_headers()
        handler.wfile.write(buf.read())
    except Exception as e:
        handler._json(500, {"error": str(e)})


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        router.dispatch(self, "GET", urlparse(self.path).path)

    def do_POST(self) -> None:
        router.dispatch(self, "POST", urlparse(self.path).path)

    def _json(self, code: int, data: object) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


if __name__ == "__main__":
    print(f"Servidor en http://{HOST}:{PORT}")
    http.server.HTTPServer((HOST, PORT), Handler).serve_forever()
