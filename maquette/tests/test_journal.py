import pytest

from maquette import journal


def entry(seq, op="create_box", **kw):
    return journal.make_entry(seq, op, kw.pop("params", {"corner": [0, 0, 0]}),
                              "test", **kw)


def test_append_and_read_round_trip(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    journal.append(path, entry(1))
    journal.append(path, entry(2, op="move", params={"ids": ["m1"]}))
    entries = list(journal.read_entries(path))
    assert [e["seq"] for e in entries] == [1, 2]
    assert entries[1]["op"] == "move"
    assert journal.last_seq(path) == 2


def test_read_after_seq(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    for seq in range(1, 5):
        journal.append(path, entry(seq))
    assert [e["seq"] for e in journal.read_entries(path, after_seq=2)] == [3, 4]


def test_truncated_final_line_is_tolerated(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    journal.append(path, entry(1))
    journal.append(path, entry(2))
    with open(path, "a", encoding="utf-8") as handle:
        handle.write('{"v":1,"seq":3,"op":"crea')  # crash mid-append
    entries = list(journal.read_entries(path))
    assert [e["seq"] for e in entries] == [1, 2]


def test_corruption_in_the_middle_raises(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    journal.append(path, entry(1))
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("garbage line\n")
    journal.append(path, entry(3))
    with pytest.raises(journal.JournalError):
        list(journal.read_entries(path))


def test_missing_journal_yields_nothing(tmp_path):
    assert list(journal.read_entries(str(tmp_path / "nope.jsonl"))) == []


def test_entry_summary_is_speakable():
    line = journal.entry_summary(entry(7, obj_id="m3", name="tower base"))
    assert line == "7: create_box m3 tower base"
    undo_line = journal.entry_summary(
        entry(9, op="delete", params={"ids": ["m3"]}, undo_of=7))
    assert "(undo of 7)" in undo_line
    script = entry(11, op="script",
                   params={"code": "x", "intent": "make a stair"})
    assert "make a stair" in journal.entry_summary(script)
