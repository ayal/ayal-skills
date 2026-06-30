# ayal-skills

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace — a
small collection of skills I find useful. Install the whole marketplace once, then
pick the plugins you want.

## Install

Pick whichever fits your setup. (Replace `ayal/ayal-skills` with this repo's
`owner/name` if you forked it.)

### Claude Code plugin (native)

```
/plugin marketplace add ayal/ayal-skills
/plugin install recall@ayal-skills
```

Update later with `/plugin marketplace update ayal-skills`.

### `npx skills` (universal — Claude Code, Cursor, Codex, Gemini CLI, …)

The [`npx skills`](https://github.com/vercel-labs/skills) tool works across 70+
agents and discovers the skills in this repo via its plugin manifest:

```
npx skills add ayal/ayal-skills
```

It auto-detects your agent and installs non-interactively. Update later with
`npx skills update`.

## Plugins

### `recall`

Find a past conversation by **what it was about**, and get told exactly how to resume
it — which project it lived in, when it happened, and the resume command.

Once installed, just describe the conversation:

```
/recall the session where we built the astro todos app and hit the method-verb issue
/recall when I was debugging the AC unit's local network control
```

**Optimized for Claude Code:** it searches your local transcripts
(`~/.claude/projects/**/*.jsonl`) via a deterministic helper (`search.py`) so it's fast
and cheap on tokens — the model only turns your fuzzy prompt into search terms and
confirms the match. It reports the title, project/cwd, date range, and both ways to
resume (terminal `claude --resume <id>` or in-session `/resume`).

**Other agents (Codex, Cursor, Gemini, Antigravity, …):** the skill falls back to a
general method — it locates that agent's own history store, searches it, and reports
results using that agent's resume mechanism. Best-effort, and honest when it can't
find or parse the store.

**Privacy:** everything runs locally against transcripts already on your machine.
Nothing is uploaded.

## Repo layout

```
ayal-skills/
├── .claude-plugin/
│   └── marketplace.json        # lists the plugins in this marketplace
├── plugins/
│   └── recall/
│       ├── .claude-plugin/
│       │   └── plugin.json      # the recall plugin manifest
│       └── skills/
│           └── recall/
│               ├── SKILL.md     # instructions Claude follows
│               └── search.py    # transcript scanner
└── README.md
```

## Adding more skills

Drop a new plugin folder under `plugins/<name>/` (with its own
`.claude-plugin/plugin.json` and a `skills/<name>/SKILL.md`), then add an entry to
the `plugins` array in `.claude-plugin/marketplace.json`. Commit and push — friends
get it on the next `/plugin marketplace update`.
