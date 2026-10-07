#!/usr/bin/env python3
"""Minimal Runway API client for video-production. Stdlib only; reads RUNWAYML_API_SECRET.

Usage:
  runway.py run <endpoint> <body.json> --out <path> [--out <path2> ...]
      Submit a generation (e.g. /v1/image_to_video), wait for it, download every output.
      Any string in the body of the form "local:<path>" is uploaded first and replaced
      with its runway:// URI, so keyframes and references can stay on disk.
      Prints {"id", "status", "outputs": [paths], "estimatedCost"} as JSON.
  runway.py submit <endpoint> <body.json>     Submit only; prints {"id", "estimatedCost"}.
  runway.py wait <task-id> --out <path>       Wait for an existing task and download it.
  runway.py upload <file>                     Ephemeral upload; prints the runway:// URI (valid 24h).
  runway.py get <path>                        GET any endpoint (e.g. /v1/organization).

Body files are JSON. Exit code is non-zero on HTTP errors and FAILED tasks; the failure
code and message go to stderr so the agent can decide whether to rewrite the prompt.
"""
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = os.environ.get("RUNWAY_BASE_URL", "https://api.dev.runwayml.com")
VERSION = "2024-11-06"


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def secret():
    key = os.environ.get("RUNWAYML_API_SECRET") or os.environ.get("RUNWAY_SKILLS_API_SECRET")
    if not key:
        die("RUNWAYML_API_SECRET is not set")
    return key


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {secret()}",
            "X-Runway-Version": VERSION,
            "Content-Type": "application/json",
        },
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code == 429 or e.code >= 500:
                time.sleep(min(60, 5 * 2**attempt))
                continue
            die(f"HTTP {e.code} on {method} {path}: {detail}")
    die(f"Gave up on {method} {path} after retries")


def multipart(fields, file_path):
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    ctype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    name = os.path.basename(file_path)
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n".encode()
    )
    with open(file_path, "rb") as f:
        parts.append(f.read())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def upload(file_path):
    if not os.path.isfile(file_path):
        die(f"No such file: {file_path}")
    slot = api("POST", "/v1/uploads", {"filename": os.path.basename(file_path), "type": "ephemeral"})
    body, ctype = multipart(slot["fields"], file_path)
    req = urllib.request.Request(slot["uploadUrl"], data=body, method="POST", headers={"Content-Type": ctype})
    try:
        urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        die(f"Upload of {file_path} failed: HTTP {e.code} {e.read().decode(errors='replace')}")
    return slot["runwayUri"]


def resolve_locals(node, base_dir):
    """Replace "local:<path>" strings with runway:// URIs, uploading each file once."""
    cache = {}

    def walk(n):
        if isinstance(n, dict):
            return {k: walk(v) for k, v in n.items()}
        if isinstance(n, list):
            return [walk(v) for v in n]
        if isinstance(n, str) and n.startswith("local:"):
            p = os.path.normpath(os.path.join(base_dir, n[len("local:"):]))
            if p not in cache:
                cache[p] = upload(p)
            return cache[p]
        return n

    return walk(node)


def wait(task_id):
    delay = 5
    while True:
        task = api("GET", f"/v1/tasks/{task_id}")
        status = task.get("status")
        if status == "SUCCEEDED":
            return task
        if status in ("FAILED", "CANCELLED"):
            die(json.dumps({"id": task_id, "status": status, "failureCode": task.get("failureCode"),
                            "failure": task.get("failure")}))
        time.sleep(delay)
        delay = min(delay + 5, 20)


def download(urls, outs):
    if len(outs) < len(urls):
        # More outputs than paths: suffix the last path with an index.
        stem, ext = os.path.splitext(outs[-1])
        outs = outs[:-1] + [f"{stem}-{i}{ext}" for i in range(len(urls) - len(outs) + 1)]
    saved = []
    for url, out in zip(urls, outs):
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        urllib.request.urlretrieve(url, out)
        saved.append(out)
    return saved


def take_outs(args):
    outs, rest, i = [], [], 0
    while i < len(args):
        if args[i] == "--out":
            outs.append(args[i + 1])
            i += 2
        else:
            rest.append(args[i])
            i += 1
    return rest, outs


def load_body(path):
    with open(path) as f:
        return resolve_locals(json.load(f), os.path.dirname(os.path.abspath(path)))


def main():
    args, outs = take_outs(sys.argv[1:])
    if not args:
        die(__doc__)
    cmd = args[0]
    if cmd == "run" and len(args) == 3 and outs:
        created = api("POST", args[1], load_body(args[2]))
        task = wait(created["id"])
        print(json.dumps({"id": created["id"], "status": task["status"],
                          "outputs": download(task.get("output", []), outs),
                          "estimatedCost": created.get("estimatedCost")}))
    elif cmd == "submit" and len(args) == 3:
        created = api("POST", args[1], load_body(args[2]))
        print(json.dumps({"id": created["id"], "estimatedCost": created.get("estimatedCost")}))
    elif cmd == "wait" and len(args) == 2 and outs:
        task = wait(args[1])
        print(json.dumps({"id": args[1], "status": task["status"],
                          "outputs": download(task.get("output", []), outs)}))
    elif cmd == "upload" and len(args) == 2:
        print(upload(args[1]))
    elif cmd == "get" and len(args) == 2:
        print(json.dumps(api("GET", args[1]), indent=2))
    else:
        die(__doc__)


if __name__ == "__main__":
    main()
