---
name: recall
description: Find a past coding-agent conversation by what it was about, and report how to resume it. Use when the user wants to locate an earlier session/conversation/chat from memory — e.g. "/recall the conv where we built the astro app", "find the conversation about X", "which session did we debug Y in", "rewind to when we set up Z". Optimized for Claude Code (reads local transcripts); falls back to a general method for other agents (Codex, Cursor, Gemini, Antigravity, …).
---

# recall — find a past conversation and how to resume it

Locate the earlier conversation(s) the user is describing and tell them exactly how to
get back into each one: which project/workspace it lived in, when it happened, and the
resume command. Lead with the best match; keep the report tight.

## Step 0 — which agent are you?

You know what you are. Branch on it:
- **Claude Code** → use **Path A** (optimized: bundled helper + real `claude --resume`).
- **Any other agent** (Codex, Cursor, Gemini CLI, Antigravity, Windsurf, …) → use
  **Path B** (general method for your own history store).

Either way, the search/report shape is the same: derive good keywords → find candidate
sessions → confirm the top hit → report title, project, dates, and how to resume.

---

## Path A — Claude Code (optimized)

Transcripts are JSONL at `~/.claude/projects/<slug>/<sessionId>.jsonl`. The `<slug>` is
the working dir with `/`→`-`; the filename is the **session id**; inside, `aiTitle` is
the short title, `cwd` the working dir, `gitBranch` the branch, `timestamp` the dates.

1. **Derive keywords** from the request — distinctive nouns plus obvious
   synonyms/variants (more angles → better ranking). Drop filler ("the", "conversation",
   "where we"). E.g. "the astro wix app where method verbs broke" → `astro wix headless
   todo velo method verb PATCH DELETE GET POST SSR route`.

2. **Run the bundled helper.** `search.py` ships in this skill's own directory (the same
   folder as this SKILL.md — depending on install that's the plugin dir,
   `~/.claude/skills/recall/`, or `.agents/skills/recall/`). Resolve its path and run:
   ```bash
   python3 <path-to>/search.py --limit 8 <keyword> <keyword> ...
   ```
   It prints JSON sorted best-first: each result has `title`, `session_id`,
   `project_slug`, `cwd`, `git_branch`, timestamps, `mtime`, `first_user_prompt`,
   `snippet`. If you can't locate the script, fall back to grepping
   `~/.claude/projects/**/*.jsonl` yourself (match keywords; pull `aiTitle`/`cwd`/
   `timestamp` from matching files).

3. **Confirm the match.** Top hit is usually right. If ambiguous, read the candidate
   transcript `path` (grep for the distinctive term) before claiming it. For a large
   result set, delegate the confirmation read to a fast subagent to keep it cheap.

4. **If nothing matches**, broaden keywords and re-run; say what you searched if empty.

**Resume instructions to give:**
- Terminal: `cd "<cwd>" && claude --resume <session_id>`
- In-session: run `/resume` and pick the conversation by its title.
- Include the transcript `path` (it's clickable).

---

## Path B — other agents (general method)

You're not Claude Code, so there's no bundled scanner for your history format. Work it
out for your environment:

1. **Locate your history store.** Find where *this* agent persists past conversations,
   then **verify the location exists** (`ls` it) before trusting it. Likely spots — treat
   as hints, not gospel:
   - **Codex CLI** → `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-*.jsonl` (JSONL).
   - **Gemini CLI** → under `~/.gemini/` (e.g. `~/.gemini/tmp/<hash>/` logs/checkpoints).
   - **Antigravity** → under `~/.gemini/antigravity*/` or its own app-support dir.
   - **Cursor / Windsurf / other VS Code forks** → SQLite at
     `~/Library/Application Support/<App>/User/workspaceStorage/*/state.vscdb` (and
     `globalStorage/`); query with `sqlite3`.
   - Otherwise: check the agent's docs/config dir under `~`, `~/.config/`, or
     `~/Library/Application Support/`.

2. **Search it** with whatever tools you have: `grep`/`rg` over JSONL or log files;
   `sqlite3 <db> "SELECT ..."` for VS Code-style stores. Use the same keyword-derivation
   as Path A. Pull out, per candidate: a title or first user prompt, the project/workspace
   path, a timestamp, and any session/conversation id.

3. **Confirm** the best candidate by reading a bit of it before claiming it matches.

4. **Report how to resume using THIS agent's own mechanism** — not `claude --resume`.
   If the agent has a resume command/UI, give that; if you're unsure, point the user to
   the conversation file/id and where it lives, and say plainly that you couldn't confirm
   the exact resume path. **Don't invent a resume command.**

If you can't find or parse the history store, say so, say where you looked, and stop —
don't guess.

---

## Reporting (both paths)

For each conversation reported:
- **Title** + a one-line summary of what it covered.
- **Project/workspace** path.
- **When** — a human date range.
- **How to resume** — the right command for the agent you're in.
- The transcript/file **path**.

If several plausibly match, list the top few ranked, say which you think is best and why,
and let the user choose. The user wants to jump back in — not read a wall of text.
