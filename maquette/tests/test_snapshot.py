import json

from maquette import snapshot


COMMANDS = [
    'box 10 10 30 name "tower base"',
    "sphere radius 4 at 20,0,0",
    "rect 8 6 at -10,0",
    "extrude m3 height 9",
    "move m1 by 0,0,5",
    "rotate m2 by 30 around 20,0,0",
    "copy m1 by 15,0,0 count 2",
    'group m1 m6 name "towers"',
    "layer add Walls",
    "put m2 on Walls",
]


def build(engine):
    for command in COMMANDS:
        engine.run_text(command)
    engine.undo_steps(2)


def test_snapshot_plus_tail_equals_full_replay(engine, project):
    build(engine)
    # Force a snapshot mid-history, then add more ops on top.
    scene_mid = snapshot.load_scene(project)
    snapshot.write_snapshot(project, scene_mid)
    engine.run_text("box 2 2 2 at 50,0,0")
    engine.run_text("move last by 0,5,0")

    derived = snapshot.load_scene(project)        # snapshot + tail
    replayed = snapshot.replay_scene(project)     # journal only
    assert json.dumps(derived.to_dict(), sort_keys=True) == \
        json.dumps(replayed.to_dict(), sort_keys=True)


def test_deleting_snapshot_loses_nothing(engine, project):
    build(engine)
    with_cache = snapshot.load_scene(project).to_dict()
    snapshot.drop_snapshot(project)
    without_cache = snapshot.load_scene(project).to_dict()
    assert json.dumps(with_cache, sort_keys=True) == \
        json.dumps(without_cache, sort_keys=True)


def test_stale_snapshot_ahead_of_journal_is_discarded(engine, project):
    build(engine)
    snapshot.write_snapshot(project, snapshot.load_scene(project))
    # Simulate a journal restored from an older backup: truncate it.
    entries = open(project.journal_path, encoding="utf-8").readlines()
    with open(project.journal_path, "w", encoding="utf-8") as handle:
        handle.writelines(entries[:3])
    scene = snapshot.load_scene(project)
    assert scene.applied_seq == 3


def test_snapshot_writes_automatically_after_enough_ops(engine, project):
    for index in range(snapshot.SNAPSHOT_EVERY + 1):
        engine.run_text("box 1 1 1 at {0},0,0".format(index * 2))
    data = json.load(open(project.snapshot_path, encoding="utf-8"))
    assert data["upto_seq"] >= snapshot.SNAPSHOT_EVERY
