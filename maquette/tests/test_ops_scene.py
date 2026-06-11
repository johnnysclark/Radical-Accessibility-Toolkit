import pytest

from maquette import geom, ops
from maquette.scene import Scene, SceneError


def run(engine, text):
    return engine.run_text(text)


def test_validate_box_allocates_id_name_layer(engine):
    result = run(engine, "box 10 10 30")
    assert "m1" in result["lines"][0]
    scene = engine.scene()
    obj = scene.objects["m1"]
    assert obj["name"] == "box 1"
    assert obj["layer"] == "MAQ::Default"
    assert obj["fingerprint"]["bbox"] == [[0, 0, 0], [10, 10, 30]]
    assert obj["fingerprint"]["quality"] == "exact"


def test_custom_layer_is_namespaced(engine):
    run(engine, "box 1 1 1 layer Walls")
    assert engine.scene().objects["m1"]["layer"] == "MAQ::Walls"


def test_name_lookup_and_last(engine):
    run(engine, 'box 1 1 1 name "tower base"')
    run(engine, "sphere radius 2 at 10,0,0")
    scene = engine.scene()
    assert scene.find("tower base")["id"] == "m1"
    assert scene.find("last")["id"] == "m2"
    assert scene.find("m1")["name"] == "tower base"


def test_ambiguous_name_raises(engine):
    run(engine, 'box 1 1 1 name "wall"')
    run(engine, 'box 2 2 2 at 5,0,0 name "wall"')
    with pytest.raises(SceneError) as exc:
        engine.scene().find("wall")
    assert "m1" in str(exc.value) and "m2" in str(exc.value)


def test_validation_errors_speak(engine):
    with pytest.raises(ops.OpError):
        engine.run_op({"op": "create_box", "params": {"corner": [0, 0, 0],
                                                      "size": [1, 1]}})
    with pytest.raises(ops.OpError) as exc:
        engine.run_op({"op": "move", "params": {"ids": ["m99"],
                                                "vector": [1, 0, 0]}})
    assert "m99" in str(exc.value)


def test_move_updates_bbox(engine):
    run(engine, "box 10 10 10")
    run(engine, "move m1 by 5,0,0")
    assert engine.scene().objects["m1"]["fingerprint"]["bbox"] == \
        [[5, 0, 0], [15, 10, 10]]


def test_rotate_freezes_center_and_degrades_quality(engine):
    run(engine, "box 10 10 10")
    run(engine, "rotate m1 by 45")
    entries = engine.entries()
    assert entries[-1]["params"]["center"] == [5.0, 5.0, 5.0]
    obj = engine.scene().objects["m1"]
    assert obj["fingerprint"]["quality"] == "approx"


def test_rotate_90_bbox_is_correct(engine):
    run(engine, "box 20 10 5")
    run(engine, "rotate m1 by 90 around 0,0,0")
    box = engine.scene().objects["m1"]["fingerprint"]["bbox"]
    assert [round(v, 6) for v in box[0]] == [-10, 0, 0]
    assert [round(v, 6) for v in box[1]] == [0, 20, 5]


def test_scale_around_center(engine):
    run(engine, "box 10 10 10")
    run(engine, "scale m1 by 2")
    box = engine.scene().objects["m1"]["fingerprint"]["bbox"]
    assert box == [[-5, -5, -5], [15, 15, 15]]


def test_copy_creates_speakable_clones(engine):
    run(engine, 'box 5 5 5 name "pier"')
    result = run(engine, "copy m1 by 10,0,0 count 2")
    assert len(result["lines"]) == 2
    scene = engine.scene()
    assert scene.objects["m2"]["fingerprint"]["bbox"] == [[10, 0, 0], [15, 5, 5]]
    assert scene.objects["m3"]["fingerprint"]["bbox"] == [[20, 0, 0], [25, 5, 5]]
    # Auto-names count per kind; "pier" was custom, so clones start at box 1.
    assert scene.objects["m2"]["name"] == "box 1"
    assert scene.objects["m3"]["name"] == "box 2"


def test_boolean_consumes_inputs_and_is_pending(engine):
    run(engine, "box 10 10 10")
    run(engine, "sphere radius 3 at 10,5,5")
    run(engine, "union m1 m2")
    scene = engine.scene()
    assert scene.objects["m1"]["status"] == "consumed"
    assert scene.objects["m2"]["status"] == "consumed"
    union = scene.objects["m3"]
    assert union["status"] == "alive"
    assert union["pending"] is True
    assert union["fingerprint"]["bbox"] == [[0, 0, 0], [13, 10, 10]]


def test_cannot_reuse_consumed_objects(engine):
    run(engine, "box 1 1 1")
    run(engine, "box 1 1 1 at 0.5,0,0")
    run(engine, "union m1 m2")
    with pytest.raises(ops.OpError) as exc:
        run(engine, "move m1 by 1,0,0")
    assert "consumed" in str(exc.value)


def test_extrude_fingerprint_from_source(engine):
    run(engine, "rect 10 6")
    run(engine, "extrude m1 height 12")
    obj = engine.scene().objects["m2"]
    assert obj["fingerprint"]["bbox"] == [[0, 0, 0], [10, 6, 12]]


def test_group_and_ungroup(engine):
    run(engine, "box 1 1 1")
    run(engine, "box 1 1 1 at 2,0,0")
    run(engine, 'group m1 m2 name "piers"')
    scene = engine.scene()
    assert scene.groups["g1"]["members"] == ["m1", "m2"]
    assert scene.objects["m1"]["group"] == "g1"
    run(engine, "ungroup g1")
    scene = engine.scene()
    assert scene.groups == {}
    assert scene.objects["m1"]["group"] is None


def test_script_requires_intent(engine):
    with pytest.raises(ops.OpError) as exc:
        engine.run_op({"op": "script", "params": {"code": "print(1)"}})
    assert "intent" in str(exc.value)


def test_mirror_bbox(engine):
    run(engine, "box 10 10 10 at 5,0,0")
    run(engine, "mirror m1 across 0,0 to 0,10")
    box = engine.scene().objects["m1"]["fingerprint"]["bbox"]
    assert [round(v, 6) for v in box[0]] == [-15, 0, 0]
    assert [round(v, 6) for v in box[1]] == [-5, 10, 10]


def test_counters_survive_user_names(engine):
    run(engine, 'box 1 1 1 name "alpha"')
    run(engine, "box 1 1 1 at 3,0,0")
    run(engine, "box 1 1 1 at 6,0,0")
    scene = engine.scene()
    # Auto-names count per kind and skip custom-named objects.
    assert scene.objects["m2"]["name"] == "box 1"
    assert scene.objects["m3"]["name"] == "box 2"


def test_geom_rotate_point_sanity():
    rotated = geom.rotate_point([1, 0, 0], [0, 0, 0], 90, [0, 0, 1])
    assert [round(v, 9) for v in rotated] == [0, 1, 0]
    mirrored = geom.mirror_point([3, 1, 2], [0, 0, 0], [1, 0, 0])
    assert mirrored == [-3, 1, 2]
