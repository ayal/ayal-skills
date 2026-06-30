#!/usr/bin/env python3
"""
recall/search.py — scan local Claude Code conversation transcripts and rank
them against a set of keywords.

Transcripts live at ~/.claude/projects/<slug>/<sessionId>.jsonl, one JSON
object per line. We score each file by how many of the supplied keywords it
matches (distinct keywords matter more than raw frequency), then emit the top
candidates as JSON with everything needed to resume them.

Usage:
    search.py [--limit N] [--projects DIR] <keyword> [<keyword> ...]

Keywords are matched case-insensitively as substrings. Pass several; they are
OR-matched, and files matching more distinct keywords rank higher.
"""
import sys, os, json, glob, argparse, datetime

DEFAULT_PROJECTS = os.path.expanduser("~/.claude/projects")


def iter_text_blocks(msg):
    """Yield human-readable text from a transcript 'message' field."""
    if not isinstance(msg, dict):
        return
    content = msg.get("content")
    if isinstance(content, str):
        yield content
        return
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t == "text" and isinstance(b.get("text"), str):
                yield b["text"]
            elif t == "tool_result":
                c = b.get("content")
                if isinstance(c, str):
                    yield c
                elif isinstance(c, list):
                    for sub in c:
                        if isinstance(sub, dict) and isinstance(sub.get("text"), str):
                            yield sub["text"]
            elif t == "tool_use" and isinstance(b.get("input"), dict):
                yield json.dumps(b["input"])


def scan_file(path, kws):
    """Return a candidate dict for a transcript, or None if no keyword matched."""
    matched = set()
    total_hits = 0
    snippet = None
    ai_title = None
    cwd = None
    git_branch = None
    first_ts = None
    last_ts = None
    first_user_prompt = None

    try:
        with open(path, "r", errors="replace") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                # Cheap pre-filter on the raw line before parsing JSON.
                low = raw.lower()
                line_hit = [k for k in kws if k in low]
                try:
                    d = json.loads(raw)
                except Exception:
                    if line_hit:
                        for k in line_hit:
                            matched.add(k)
                            total_hits += low.count(k)
                    continue

                if d.get("aiTitle"):
                    ai_title = d["aiTitle"]
                if cwd is None and d.get("cwd"):
                    cwd = d["cwd"]
                if d.get("gitBranch"):
                    git_branch = d["gitBranch"]
                ts = d.get("timestamp")
                if ts:
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts

                msg = d.get("message")
                role = msg.get("role") if isinstance(msg, dict) else None
                text = " ".join(iter_text_blocks(msg)) if msg else ""

                if first_user_prompt is None and role == "user" and text.strip() \
                        and not text.lstrip().startswith("<"):
                    first_user_prompt = text.strip()[:300]

                if line_hit:
                    haystack = (text or raw).lower()
                    for k in line_hit:
                        matched.add(k)
                        total_hits += haystack.count(k)
                    if snippet is None and text.strip():
                        # Grab a window around the first keyword occurrence.
                        tl = text.lower()
                        pos = min((tl.find(k) for k in line_hit if k in tl),
                                  default=-1)
                        if pos >= 0:
                            start = max(0, pos - 120)
                            snippet = text[start:pos + 200].strip().replace("\n", " ")
    except Exception:
        return None

    if not matched:
        return None

    return {
        "score": len(matched) * 1000 + total_hits,
        "distinct_keywords": sorted(matched),
        "total_hits": total_hits,
        "title": ai_title,
        "session_id": os.path.splitext(os.path.basename(path))[0],
        "project_slug": os.path.basename(os.path.dirname(path)),
        "cwd": cwd,
        "git_branch": git_branch,
        "first_timestamp": first_ts,
        "last_timestamp": last_ts,
        "mtime": datetime.datetime.fromtimestamp(
            os.path.getmtime(path)).isoformat(timespec="seconds"),
        "first_user_prompt": first_user_prompt,
        "snippet": snippet,
        "path": path,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--projects", default=DEFAULT_PROJECTS)
    ap.add_argument("keywords", nargs="+")
    args = ap.parse_args()

    kws = [k.lower() for k in args.keywords if k.strip()]
    files = glob.glob(os.path.join(args.projects, "*", "*.jsonl"))

    results = []
    for p in files:
        c = scan_file(p, kws)
        if c:
            results.append(c)

    results.sort(key=lambda r: (r["score"], r["mtime"]), reverse=True)
    out = {
        "keywords": kws,
        "transcripts_scanned": len(files),
        "match_count": len(results),
        "results": results[: args.limit],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
