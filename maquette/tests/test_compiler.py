"""Compiled snippets: syntactically valid Python with the right calls.

The engine fixture builds real validated entries (ids resolved,
defaults frozen) and we compile those, exactly as the live backend
would.
"""

from maquette import compiler, journal, ops


def entry_for(engine, text):
    engine.run_text(text)
    return engine.entries()[-1]


def compiled(engine, text):
    code = compiler.compile_entry(entry_for(engine, text))
    compile(code, "<snippet>", "exec")  # must be valid Python
    return code


def test_box_emits_eight_corners(engine):
    code = compiled(engine, "box 10 10 30 at 1,2,3")
    assert "rs.AddBox(" in code
    assert "[11, 12, 33]" in code.replace(".0", "")
    assert "__maq_created__.append(g)" in code


def test_arc_point_order_start_end_interior(engine):
    code = compiled(engine, "arc 0,0 5,5 10,0")
    head = code.splitlines()[0]
    assert head.index("[0.0, 0.0, 0.0]") < head.index("[10.0, 0.0, 0.0]")
    assert head.index("[10.0, 0.0, 0.0]") < head.index("[5.0, 5.0, 0.0]")


def test_polyline_closed_repeats_first_point(engine):
    code = compiled(engine, "polyline 0,0 10,0 10,10 closed")
    assert code.count("[0.0, 0.0, 0.0]") == 2


def test_cone_apex_above_base(engine):
    code = compiled(engine, "cone radius 3 height 9 at 1,1,0")
    assert "rs.AddCone([1.0, 1.0, 0.0], [1.0, 1.0, 9.0], 3.0" in code


def test_transforms_find_by_maq_id(engine):
    engine.run_text("box 5 5 5")
    code = compiler.compile_entry(entry_for(engine, "move m1 by 0,0,10"))
    assert "__maq__.find(['m1'])" in code
    assert "rs.MoveObjects" in code
    code = compiler.compile_entry(entry_for(engine, "rotate m1 by 45"))
    assert "rs.RotateObjects" in code
    assert "copy=False" in code


def test_mirror_uses_general_xform(engine):
    engine.run_text("box 5 5 5")
    code = compiler.compile_entry(entry_for(engine, "mirror m1 across 0,0 to 0,10"))
    assert "rs.XformMirror" in code
    assert "rs.TransformObjects" in code


def test_difference_keep_and_cut_lists(engine):
    engine.run_text("box 10 10 10")
    engine.run_text("sphere radius 3 at 5,5,10")
    code = compiler.compile_entry(entry_for(engine, "difference m1 minus m2"))
    assert "rs.BooleanDifference(__maq__.find(['m1']), __maq__.find(['m2']))" \
        in code


def test_copy_tags_each_clone(engine):
    engine.run_text("box 5 5 5")
    code = compiler.compile_entry(entry_for(engine, "copy m1 by 10,0,0 count 2"))
    compile(code, "<snippet>", "exec")
    assert code.count("rs.CopyObjects") == 2
    assert "__maq__.tag(made, 'm2'" in code
    assert "__maq__.tag(made, 'm3'" in code
    assert "[20.0, 0.0, 0.0]" in code  # second batch offset doubled


def test_restore_recreates_and_replays_transforms(engine):
    engine.run_text("box 10 10 10")
    engine.run_text("move m1 by 5,0,0")
    engine.run_text("delete m1")
    engine.undo_steps()
    restore_entry = engine.entries()[-1]
    assert restore_entry["op"] == "restore"
    code = compiler.compile_entry(restore_entry)
    compile(code, "<snippet>", "exec")
    assert "rs.AddBox(" in code
    assert "rs.MoveObjects(made, [5.0, 0.0, 0.0])" in code
    assert "__maq__.tag(made, 'm1'" in code


def test_script_is_seeded_for_replay(engine):
    engine.run_op({"op": "script", "params": {
        "code": "print('hi')", "intent": "say hi"}})
    code = compiler.compile_entry(engine.entries()[-1])
    assert "random.seed(1)" in code
    assert "print('hi')" in code


def test_meta_ops_compile_to_nothing():
    assert compiler.compile_entry(
        journal.make_entry(1, "noop", {"note": ""}, "test")) is None
    assert compiler.compile_entry(
        journal.make_entry(2, "reconcile",
                           {"fingerprints": {}, "backend": "live"},
                           "test")) is None


def test_every_op_has_a_builder_or_is_meta():
    covered = set(compiler._BUILDERS) | ops.NO_UNDO_OPS
    assert covered == ops.ALL_OPS


def test_layer_ops(engine):
    engine.run_text("box 1 1 1")
    code = compiler.compile_entry(entry_for(engine, "layer add Walls"))
    assert "__maq__.ensure_layer('MAQ::Walls')" in code
    code = compiler.compile_entry(entry_for(engine, "put m1 on Walls"))
    assert "rs.ObjectLayer" in code
