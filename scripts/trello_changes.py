#!/usr/bin/env python3
"""Compare complete Trello MCP exports without writing to Trello."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("board_id"), str) or not data["board_id"]:
        raise ValueError("Missing board_id")
    if not isinstance(data.get("cards"), list):
        raise ValueError("Missing cards array")
    cards = {}
    for card in data["cards"]:
        if not isinstance(card, dict) or not all(isinstance(card.get(k), str) and card[k] for k in ("id", "name", "list_id")):
            raise ValueError("Each card needs id, name and list_id")
        if card["id"] in cards:
            raise ValueError("Duplicate card ID")
        for key in ("members", "comment_ids"):
            if not isinstance(card.get(key, []), list) or not all(isinstance(v, str) for v in card.get(key, [])):
                raise ValueError(key + " must be an array of strings")
        if not isinstance(card.get("comments_complete", False), bool):
            raise ValueError("comments_complete must be boolean")
        cards[card["id"]] = card
    return data, cards


def compare(before, after):
    prev, a = load(before)
    curr, b = load(after)
    if prev["board_id"] != curr["board_id"]:
        raise ValueError("Cannot compare different boards")
    changes = []
    for cid in sorted(b.keys() - a.keys()):
        c = b[cid]
        changes.append({"kind": "new_card", "id": cid, "name": c["name"], "url": c.get("url")})
    # A missing card might indicate incomplete export, not deletion.
    for cid in sorted(b.keys() & a.keys()):
        old, new = a[cid], b[cid]
        base = {"id": cid, "name": new["name"], "url": new.get("url")}
        if old["list_id"] != new["list_id"]:
            changes.append({**base, "kind": "moved", "from": old.get("list_name") or old["list_id"], "to": new.get("list_name") or new["list_id"]})
        if set(old.get("members", [])) != set(new.get("members", [])):
            changes.append({**base, "kind": "members_changed", "from": sorted(old.get("members", [])), "to": sorted(new.get("members", []))})
        if old.get("due") != new.get("due"):
            changes.append({**base, "kind": "due_changed", "from": old.get("due"), "to": new.get("due")})
        if old.get("comments_complete") is True and new.get("comments_complete") is True:
            added = sorted(set(new.get("comment_ids", [])) - set(old.get("comment_ids", [])))
            removed = sorted(set(old.get("comment_ids", [])) - set(new.get("comment_ids", [])))
            if added:
                changes.append({**base, "kind": "comment_ids_newly_observed", "count": len(added),
                                "comment_ids": added, "requires_timestamp_verification": True})
            if removed:
                changes.append({**base, "kind": "comment_ids_missing", "count": len(removed),
                                "comment_ids": removed, "deletion_unverified": True})
    return {"board_id": curr["board_id"], "previous_capture": prev.get("captured_at"),
            "current_capture": curr.get("captured_at"), "changes": changes}


def save_atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("snapshot", help="Path to complete Trello MCP snapshot JSON")
    p.add_argument("--state-dir", default=str(Path.home() / ".local/share/brf-brief/trello"))
    p.add_argument("--preview", action="store_true", help="Do not advance baseline")
    args = p.parse_args()
    data, cards = load(args.snapshot)
    if data.get("complete_board") is not True:
        raise ValueError("Export must explicitly declare complete_board=true")
    state = Path(args.state_dir) / "latest.json"
    if state.exists():
        print(json.dumps(compare(state, args.snapshot), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"baseline_created": not args.preview, "board_id": data["board_id"],
                          "card_count": len(cards), "changes": []}, ensure_ascii=False, indent=2))
    if not args.preview:
        save_atomic(state, data)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        sys.exit(2)
