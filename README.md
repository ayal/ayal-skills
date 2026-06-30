# ayal-skills

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace — a
small collection of skills I find useful. Install the whole marketplace once, then
pick the plugins you want.

## Install

In Claude Code:

```
/plugin marketplace add ayal/ayal-skills
/plugin install recall@ayal-skills
```

(Replace `ayal/ayal-skills` with this repo's `owner/name` if you forked it.)

To update later: `/plugin marketplace update ayal-skills`.

## Plugins

### `recall`

Find a past Claude Code conversation by **what it was about**, and get told exactly
how to resume it — which project it lived in, when it happened, and the resume command.

Once installed, just describe the conversation:

```
/recall the session where we built the astro todos app and hit the method-verb issue
/recall when I was debugging the AC unit's local network control
```

It searches your local transcripts (`~/.claude/projects/**/*.jsonl`), ranks the
matches, confirms the best one, and reports the title, project/cwd, date range, and
both ways to resume (terminal `claude --resume <id>` or in-session `/resume`).

A deterministic helper (`search.py`) does the file scan so it's fast and cheap on
tokens; the model only handles turning your fuzzy prompt into search terms and
confirming the match.

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
