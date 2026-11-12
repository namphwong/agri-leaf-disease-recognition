"""Guard against leakage and ambiguous metadata in the preparation algorithm."""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_dataset import assert_integrity, connect_and_split, leaf_candidates


def record(name, label="A", leaf=None, rgb=None):
    return {"source_path": name, "label": label, "leaf_ids": [leaf or f"{label}:::{name}"],
            "sha256": f"bytes:{name}", "rgb_sha256": rgb or f"rgb:{name}", "error": ""}


def base_rows():
    return [record(f"{label}-{i}", label) for label in ("A", "B") for i in range(6)]


class DatasetPreparationTests(unittest.TestCase):
    def test_transitive_leaf_and_pixel_duplicates_stay_together(self):
        rows = base_rows()
        rows += [record("copy-a", leaf="A:::A-0", rgb="shared"),
                 record("copy-b", leaf="A:::A-1", rgb="shared")]
        connect_and_split(rows, 42)
        linked = [r for r in rows if r["source_path"] in ("A-0", "A-1", "copy-a", "copy-b")]
        self.assertEqual(len({r["group_id"] for r in linked}), 1)
        self.assertEqual(len({r["split"] for r in linked}), 1)
        self.assertEqual(sum(r["exclusion_reason"] == "exact_rgb_duplicate" for r in linked), 1)
        assert_integrity(rows, ["A", "B"])

    def test_unknown_leaf_quarantines_entire_duplicate_component(self):
        rows = base_rows()
        unknown = record("unknown", rgb="rgb:A-0")
        unknown["leaf_ids"] = []
        rows.append(unknown)
        connect_and_split(rows, 42)
        linked = [r for r in rows if r["source_path"] in ("A-0", "unknown")]
        self.assertTrue(all(r["split"] == "quarantine" for r in linked))
        self.assertTrue(all(not r["use_for_training_evaluation"] for r in linked))

    def test_conflicting_labels_are_not_silently_deduplicated(self):
        rows = base_rows() + [record("conflict", "B", rgb="rgb:A-0")]
        connect_and_split(rows, 42)
        linked = [r for r in rows if r["source_path"] in ("A-0", "conflict")]
        self.assertTrue(all("conflicting_labels" in r["quarantine_reason"] for r in linked))

    def test_three_groups_still_have_train_validation_and_test(self):
        rows = [record(str(i)) for i in range(3)]
        connect_and_split(rows, 42)
        self.assertEqual({r["split"] for r in rows}, {"train", "validation", "test"})

    def test_input_order_does_not_change_partitions(self):
        first = base_rows()
        second = copy.deepcopy(list(reversed(first)))
        connect_and_split(first, 42)
        connect_and_split(second, 42)
        by_path = lambda items: {r["source_path"]: (r["group_id"], r["split"]) for r in items}
        self.assertEqual(by_path(first), by_path(second))

    def test_ambiguous_mapping_keeps_all_same_class_candidates(self):
        mapping = {"leaf 1": ["A:::1", "A:::2", "B:::7"]}
        self.assertEqual(leaf_candidates("uuid___Leaf 1.JPG", "A", mapping), ["A:::1", "A:::2"])
        self.assertEqual(leaf_candidates("missing.JPG", "A", mapping), [])


if __name__ == "__main__":
    unittest.main()
