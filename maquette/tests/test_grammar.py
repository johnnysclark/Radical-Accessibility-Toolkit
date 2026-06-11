import pytest

from maquette import grammar
from maquette.grammar import GrammarError


def test_box_with_clauses():
    op = grammar.parse('box 10 10 30 at 0,0,0 name "tower base" layer Massing')
    assert op["op"] == "create_box"
    assert op["params"]["size"] == [10.0, 10.0, 30.0]
    assert op["params"]["corner"] == [0.0, 0.0, 0.0]
    assert op["name"] == "tower base"
    assert op["layer"] == "Massing"


def test_box_defaults_to_origin():
    op = grammar.parse("box 5 5 5")
    assert op["params"]["corner"] == [0.0, 0.0, 0.0]


def test_line_two_d_coordinates_get_zero_z():
    op = grammar.parse("line 0,0 to 10,0")
    assert op["params"]["start"] == [0.0, 0.0, 0.0]
    assert op["params"]["end"] == [10.0, 0.0, 0.0]


def test_polyline_closed():
    op = grammar.parse("polyline 0,0 10,0 10,10 closed")
    assert op["op"] == "create_polyline"
    assert len(op["params"]["points"]) == 3
    assert op["params"]["closed"] is True


def test_circle_word_order_is_forgiving():
    a = grammar.parse("circle radius 5 at 1,2,3")
    b = grammar.parse("circle at 1,2,3 radius 5")
    c = grammar.parse("circle 5 at 1,2,3")
    assert a["params"] == b["params"] == c["params"]


def test_move_by_vector():
    op = grammar.parse("move m1 m2 by 0,0,10")
    assert op["op"] == "move"
    assert op["params"]["ids"] == ["m1", "m2"]
    assert op["params"]["vector"] == [0.0, 0.0, 10.0]


def test_rotate_with_axis_word():
    op = grammar.parse("rotate m1 by 45 around 0,0,0 axis y")
    assert op["params"]["angle"] == 45.0
    assert op["params"]["axis"] == [0, 1, 0]
    assert op["params"]["center"] == [0.0, 0.0, 0.0]


def test_rotate_center_optional():
    op = grammar.parse("rotate m1 by 90")
    assert "center" not in op["params"]


def test_difference_keep_minus_cut():
    op = grammar.parse('difference "tower base" minus m4 m5')
    assert op["op"] == "boolean_difference"
    assert op["params"]["keep"] == ["tower base"]
    assert op["params"]["cut"] == ["m4", "m5"]


def test_quoted_names_with_spaces_are_single_refs():
    op = grammar.parse('delete "north wall" m7')
    assert op["params"]["ids"] == ["north wall", "m7"]


def test_delete_all():
    assert grammar.parse("delete all")["params"] == {"all": True}


def test_copy_with_count():
    op = grammar.parse("copy m1 by 5,0,0 count 3")
    assert op["params"]["count"] == 3


def test_mirror_across_line():
    op = grammar.parse("mirror m1 across 0,0 to 0,10")
    assert op["op"] == "mirror"
    assert op["params"]["plane_point"] == [0.0, 0.0, 0.0]
    assert op["params"]["plane_normal"] == [-10.0, 0.0, 0.0]


def test_extrude_height_and_vector_forms():
    a = grammar.parse("extrude m3 height 12")
    assert a["params"]["height"] == 12.0
    b = grammar.parse("extrude m3 by 0,0,12")
    assert b["params"]["vector"] == [0.0, 0.0, 12.0]


def test_text_command():
    op = grammar.parse('text "north entry" at 5,5 height 2')
    assert op["params"]["text"] == "north entry"
    assert op["params"]["height"] == 2.0


def test_layer_add_and_put():
    add = grammar.parse("layer add Walls")
    assert add == {"op": "create_layer", "params": {"name": "Walls"}}
    put = grammar.parse("put m1 m2 on Walls")
    assert put["params"]["ids"] == ["m1", "m2"]
    assert put["params"]["layer"] == "Walls"


def test_rename():
    op = grammar.parse('rename m1 "tower base"')
    assert op["params"] == {"id": "m1", "name": "tower base"}


def test_aliases():
    assert grammar.parse("rectangle 4 5")["op"] == "create_rectangle"
    assert grammar.parse("subtract m1 minus m2")["op"] == "boolean_difference"


def test_errors_teach_usage():
    with pytest.raises(GrammarError) as exc:
        grammar.parse("box 10 10")
    assert "usage: box" in str(exc.value)
    with pytest.raises(GrammarError) as exc:
        grammar.parse("line 0,0 10,0")
    assert "usage: line" in str(exc.value)
    with pytest.raises(GrammarError) as exc:
        grammar.parse("frobnicate 1 2 3")
    assert "unknown command" in str(exc.value)


def test_is_command():
    assert grammar.is_command("box 1 1 1")
    assert grammar.is_command("  MOVE m1 by 1,0,0")
    assert not grammar.is_command("please make me a tower")
    assert not grammar.is_command("")
