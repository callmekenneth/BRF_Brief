import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from trello_changes import compare, load


class TrelloChangesTests(unittest.TestCase):
    def test_new_move_member_and_comment(self):
        before = {"board_id": "b", "cards": [
            {"id": "1", "name": "Garage", "list_id": "todo", "list_name": "ToDo",
             "members": ["a"], "comment_ids": ["x"], "comments_complete": True}]}
        after = {"board_id": "b", "cards": [
            {"id": "1", "name": "Garage", "list_id": "doing", "list_name": "Pågår",
             "members": ["a", "b"], "comment_ids": ["x", "y"], "comments_complete": True},
            {"id": "2", "name": "Avtal", "list_id": "todo"}]}
        with tempfile.TemporaryDirectory() as directory:
            p, q = Path(directory) / "old.json", Path(directory) / "new.json"
            p.write_text(json.dumps(before))
            q.write_text(json.dumps(after))
            kinds = {c["kind"] for c in compare(p, q)["changes"]}
            self.assertEqual(kinds, {"new_card", "moved", "members_changed", "comment_ids_newly_observed"})

    def test_incomplete_comment_history_not_called_new(self):
        a = {"board_id": "b", "cards": [
            {"id": "1", "name": "Garage", "list_id": "todo",
             "comment_ids": ["x"], "comments_complete": False}]}
        b = {"board_id": "b", "cards": [
            {"id": "1", "name": "Garage", "list_id": "todo",
             "comment_ids": ["x", "y"], "comments_complete": True}]}
        with tempfile.TemporaryDirectory() as directory:
            p, q = Path(directory) / "a", Path(directory) / "b"
            p.write_text(json.dumps(a))
            q.write_text(json.dumps(b))
            self.assertEqual(compare(p, q)["changes"], [])

    def test_removed_id_is_not_claimed_deleted(self):
        before = {"board_id": "b", "cards": [{"id": "1", "name": "Instabox", "list_id": "todo", "comments_complete": True, "comment_ids": ["old"]}]}
        after = {"board_id": "b", "cards": [{"id": "1", "name": "Instabox", "list_id": "todo", "comments_complete": True, "comment_ids": []}]}
        with tempfile.TemporaryDirectory() as directory:
            p, q = Path(directory) / "old.json", Path(directory) / "new.json"
            p.write_text(json.dumps(before))
            q.write_text(json.dumps(after))
            diff = compare(p, q)["changes"]
            self.assertEqual(diff[0]["kind"], "comment_ids_missing")
            self.assertTrue(diff[0]["deletion_unverified"])

    def test_observed_id_requires_timestamp_check(self):
        before = {"board_id": "b", "cards": [{"id": "1", "name": "Garage", "list_id": "doing", "comments_complete": True, "comment_ids": []}]}
        after = {"board_id": "b", "cards": [{"id": "1", "name": "Garage", "list_id": "doing", "comments_complete": True, "comment_ids": ["prior-post"]}]}
        with tempfile.TemporaryDirectory() as directory:
            p, q = Path(directory) / "old.json", Path(directory) / "new.json"
            p.write_text(json.dumps(before))
            q.write_text(json.dumps(after))
            diff = compare(p, q)["changes"]
            self.assertEqual(diff[0]["kind"], "comment_ids_newly_observed")
            self.assertTrue(diff[0]["requires_timestamp_verification"])

    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "a"
            p.write_text(json.dumps({"board_id": "b", "cards": [
                {"id": "1", "name": "A", "list_id": "todo"},
                {"id": "1", "name": "B", "list_id": "todo"}]}))
            with self.assertRaises(ValueError):
                load(p)


if __name__ == "__main__":
    unittest.main()
