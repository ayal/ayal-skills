---
name: recall
description: Find a past Claude Code conversation by what it was about, and report how to resume it. Use when the user wants to locate an earlier session/conversation/chat from memory — e.g. "/recall the conv where we built the astro app", "find the conversation about X", "which session did we debug Y in", "rewind to when we set up Z". Searches local transcripts across all projects.
---

# recall — find a past conversation and how to resume it

Locate the earlier Claude Code conversation(s) the user is describing and tell them
exactly how to get back into each one, which project it lived in, and when it happened.

## How conversations are stored

Transcripts are JSONL files at `~/.claude/projects/<slug>/<sessionId>.jsonl`:
- The directory `<slug>` is the working directory with `/` replaced by `-`
  (e.g. `-Users-ayalg-projects` ⇒ `/Users/ayalg/projects`).
- The filename (minus `.jsonl`) is the **session id** used to resume.
- Inside each file: an `aiTitle` field holds the short title, a `cwd` field the
  real working directory, `gitBranch` the branch, and `timestamp` fields the dates.

## Steps

1. **Derive keywords** from the user's request. Pull out the distinctive nouns and
   include obvious synonyms/variants — the more angles, the better the ranking.
   Drop filler words ("the", "conversation", "where we"). Example: a request about
   "the astro wix app where method verbs broke" → `astro wix headless todo velo
   method verb PATCH DELETE GET POST SSR route`.

2. **Run the search helper** (deterministic, fast — no model needed):
   ```bash
   python3 ~/.claude/skills/recall/search.py --limit 8 <keyword> <keyword> ...
   ```
   Quote any multi-word keyword. It prints JSON: results sorted best-first, each with
   `title`, `session_id`, `project_slug`, `cwd`, `git_branch`, timestamps, `mtime`,
   `first_user_prompt`, and a `snippet`.

3. **Confirm the match.** The top hit is usually right. If results are ambiguous or
   you need to verify a specific detail the user mentioned, read the relevant lines of
   the candidate `path` (grep the transcript for the distinctive term) before claiming
   it matches. For a large/ambiguous result set, delegate the confirmation read to a
   fast subagent (haiku) to keep it cheap.

4. **If nothing matches**, broaden: fewer/more-general keywords, or more synonyms, and
   re-run. Tell the user what you searched if you come up empty.

## Reporting back

Lead with the best match. For each conversation you report, give:
- **Title** (`aiTitle`) and a one-line summary of what it covered.
- **Project**: the `cwd` (and note the slug if useful).
- **When**: a human date range from `first_timestamp`→`last_timestamp` (and `mtime`).
- **How to resume** — both paths:
  - From a terminal: `cd "<cwd>" && claude --resume <session_id>`
  - Inside an active Claude Code session: run `/resume` and pick the conversation by
    its title.
- The transcript **path**, since it's clickable.

If several conversations plausibly match, list the top few ranked, make clear which one
you think is the best fit and why, and let the user choose.

Keep the report tight — the user wants to jump back in, not read a wall of text.
