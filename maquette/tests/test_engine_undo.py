import pytest

from maquette.ops import OpError


def run(engine, text):
    return engine.run_text(text)


def test_undo_create_deletes(engine):
    run(engine, "box 10 10 10")
    result = engine.undo_steps()
    assert any("undoing step 1" in line for line in result["lines"])
    assert engine.scene().objects["m1"]["status"] == "deleted"


def test_undo_move_is_exact_inverse(engine):
    run(engine, "box 10 10 10")
    run(engine, "move m1 by 3,4,5")
    engine.undo_steps()
    assert engine.scene().objects["m1"]["fingerprint"]["bbox"] == \
        [[0, 0, 0], [10, 10, 10]]


def test_undo_delete_restores_with_transforms(engine):
    run(engine, "box 10 10 10")
    run(engine, "move m1 by 5,0,0")
    run(engine, "delete m1")
    assert engine.scene().objects["m1"]["status"] == "deleted"
    engine.undo_steps()
    obj = engine.scene().objects["m1"]
    assert obj["status"] == "alive"
    # Restored where it was: creation plus the later move.
    assert obj["fingerprint"]["bbox"] == [[5, 0, 0], [15, 10, 10]]


def test_undo_boolean_resurrects_inputs(engine):
    run(engine, "box 10 10 10")
    run(engine, "sphere radius 3 at 10,5,5")
    run(engine, "union m1 m2")
    engine.undo_steps()
    scene = engine.scene()
    assert scene.objects["m1"]["status"] == "alive"
    assert scene.objects["m2"]["status"] == "alive"
    assert scene.objects["m3"]["status"] == "deleted"


def test_undo_walks_past_earlier_undos(engine):
    run(engine, "box 1 1 1")          # seq 1
    run(engine, "box 2 2 2 at 5,0,0")  # seq 2
    engine.undo_steps()                # undoes seq 2
    engine.undo_steps()                # must undo seq 1, not the undo
    scene = engine.scene()
    assert scene.objects["m1"]["status"] == "deleted"
    assert scene.objects["m2"]["status"] == "deleted"


def test_undo_multiple_steps(engine):
    run(engine, "box 1 1 1")
    run(engine, "box 2 2 2 at 5,0,0")
    run(engine, "box 3 3 3 at 10,0,0")
    engine.undo_steps(2)
    scene = engine.scene()
    statuses = [scene.objects[i]["status"] for i in ("m1", "m2", "m3")]
    assert statuses == ["alive", "deleted", "deleted"]


def test_undo_rename_and_layer(engine):
    run(engine, 'box 1 1 1 name "old name"')
    run(engine, 'rename m1 "new name"')
    engine.undo_steps()
    assert engine.scene().objects["m1"]["name"] == "old name"
    run(engine, "put m1 on Walls")
    engine.undo_steps()
    assert engine.scene().objects["m1"]["layer"] == "MAQ::Default"


def test_nothing_to_undo(engine):
    with pytest.raises(OpError):
        engine.undo_steps()


def test_undo_copy_removes_all_clones(engine):
    run(engine, "box 1 1 1")
    run(engine, "copy m1 by 5,0,0 count 3")
    engine.undo_steps()
    scene = engine.scene()
    assert scene.objects["m1"]["status"] == "alive"
    for clone in ("m2", "m3", "m4"):
        assert scene.objects[clone]["status"] == "deleted"


def test_journal_entries_record_undo_links(engine):
    run(engine, "box 1 1 1")
    engine.undo_steps()
    entries = engine.entries()
    assert entries[-1]["undo_of"] == 1


def test_rebuild_on_record_backend_reports(engine):
    run(engine, "box 1 1 1")
    run(engine, "move m1 by 1,0,0")
    result = engine.rebuild("record")
    assert any("rebuilt 2 journal steps" in line for line in result["lines"])


def test_export_text(engine, tmp_path):
    run(engine, 'box 10 10 30 name "tower base"')
    out = str(tmp_path / "model.txt")
    result = engine.export(out, "text")
    assert "wrote" in result["lines"][0]
    content = open(out, encoding="utf-8").read()
    assert "tower base" in content
