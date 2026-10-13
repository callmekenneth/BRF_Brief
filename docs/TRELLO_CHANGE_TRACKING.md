# Trello board change tracking (first slice)

This compares two **complete, structured snapshots** returned from Trello MCP. It never writes to Trello. Python 3 standard library only.

## Snapshot contract

A snapshot JSON object has:
- `board_id`: stable Trello board ID
- `captured_at`: ISO-8601 capture timestamp
- `complete_board: true`: only set after all board cards have been retrieved successfully
- `cards`: array of `id`, `name`, `list_id`; optional `list_name`, `url`, `members` (stable member IDs), `due`, `comment_ids` (stable Trello comment action IDs) and `comments_complete`.

Use `comments_complete: true` **only** when the full comment ID history is known for the card, not when an API returns just its newest three comments. Otherwise changes in comments will not be reported. This prevents false discoveries.

Example **fictional** (never commit real board exports):

```json
{
  "board_id": "example-board",
  "captured_at": "2026-10-13T18:00:00+02:00",
  "complete_board": true,
  "cards": [
    {
      "id": "example-card",
      "name": "Example",
      "list_id": "todo",
      "list_name": "ToDo",
      "url": "https://trello.com/c/example",
      "members": ["member-1"],
      "due": null,
      "comments_complete": false
    }
  ]
}
```

## Local usage on Spark

First get a full-board JSON export from Hermes/Trello MCP and store it **outside Git**, for example `~/.local/share/brf-brief/incoming/current.json`. Do **not** use a generated prose briefing as input; use raw, validated MCP fields. The automated MCP-to-file export is **not implemented** yet.

```bash
cd ~/git-projects/BRF_Brief
python3 -m unittest discover -s tests -v
python3 scripts/trello_changes.py ~/.local/share/brf-brief/incoming/current.json
```

The first run creates the baseline locally in `~/.local/share/brf-brief/trello/latest.json`. Subsequent successful complete exports print a JSON change report, including moves between lists, added cards, changed member IDs, due dates, and new comment IDs *only when complete comment histories exist*. `--preview` compares without advancing the baseline. A failed/partial export does not replace the baseline.

**Limitations:** This first slice has no unattended Trello MCP export, no external history API, no deleted-card detection, and no semantic summary of new comments. Snapshot comparison will detect only changes visible in both captured states (a card moved twice between runs can be missed). Treat the current output as a foundation, not a finished unattended briefing. Never commit snapshots, comments or tokens to the public repository.
