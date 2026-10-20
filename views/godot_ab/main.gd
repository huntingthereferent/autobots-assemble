extends Control
## Bounded presentation of the source-owned finite F3^3 A/B example.
##
## The integer states and A/B edges come from the Python World model.
## Screen coordinates and tween motion are EDITORIAL, not physical geometry.
## No physics nodes, no simulated contacts, no runtime source mutation.

const DATA_PATH := "res://data/finite_f3_phi012.json"
const SCHEMA := "ab-native-finite-godot/v1"
const MOVE_SECONDS := 0.32
const A_COLOR := Color(0.31, 0.86, 0.89)
const B_COLOR := Color(0.71, 0.60, 1.0)
const BG := Color(0.035, 0.055, 0.093)
const MIDDLE := Color(0.13, 0.18, 0.28)
const MUTED := Color(0.62, 0.70, 0.79)

var _source: Dictionary = {}
var _rows: Dictionary = {}
var _ordered: Array = []
var _positions: Dictionary = {}
var _current: String = ""
var _inspected: String = ""
var _history: Array = []
var _anim_from: String = ""
var _anim_to: String = ""
var _anim_time: float = -1.0
var _demo_playing: bool = false
var _demo_index: int = 0
var _error: String = ""


func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP
    set_process(true)
    set_process_unhandled_key_input(true)
    if not _load_native_data():
        return
    resized.connect(queue_redraw)
    queue_redraw()


func _fail(reason: String) -> bool:
    _error = reason
    _rows.clear()
    _demo_playing = false
    push_error("A/B source projection refused: " + reason)
    queue_redraw()
    if DisplayServer.get_name() == "headless":
        get_tree().quit(2)
    return false


func _key(s: Array) -> String:
    return str(int(s[0])) + "," + str(int(s[1])) + "," + str(int(s[2]))


func _valid_state(s: Variant) -> bool:
    if not (s is Array) or s.size() != 3:
        return false
    for v in s:
        if typeof(v) != TYPE_INT and typeof(v) != TYPE_FLOAT:
            return false
        if v != 0 and v != 1 and v != 2:
            return false
    return true


func _step(s: Array, action: String) -> Array:
    var x := int(s[0])
    var y := int(s[1])
    var z := int(s[2])
    if action == "A":
        return [(x + 1) % 3, y, z]
    return [x, (y + x + 1) % 3, (z + int(_source["phi"][y])) % 3]


func _load_native_data() -> bool:
    var f := FileAccess.open(DATA_PATH, FileAccess.READ)
    if f == null:
        return _fail("missing complete native finite transition dataset")
    var parsed: Variant = JSON.parse_string(f.get_as_text())
    if not (parsed is Dictionary):
        return _fail("dataset is not a JSON object")
    _source = parsed
    if (_source.get("schema") != SCHEMA
            or _source.get("source") != "work.arc_like_maze.math.World"
            or _source.get("phi") != [0, 1, 2]
            or _source.get("depth") != 3
            or _source.get("origin") != [0, 0, 0]
            or _source.get("state_count") != 27
            or _source.get("positions") != "editorial BFS-depth projection; no physical distance claim"):
        return _fail("model identity/boundary mismatch")
    var nodes: Variant = _source.get("nodes")
    if not (nodes is Array) or nodes.size() != 27:
        return _fail("wrong finite node count")
    for row in nodes:
        if not (row is Dictionary) or not _valid_state(row.get("state")):
            return _fail("invalid native state row")
        var state: Array = row["state"]
        var k := _key(state)
        if _rows.has(k):
            return _fail("duplicated native state")
        for action in ["A", "B"]:
            if not _valid_state(row.get(action)) or row[action] != _step(state, action):
                return _fail("A/B edge contradicts source finite rules")
        if typeof(row.get("depth")) != TYPE_INT and typeof(row.get("depth")) != TYPE_FLOAT:
            return _fail("invalid graph depth")
        if int(row["depth"]) != row["depth"] or int(row["depth"]) < 0:
            return _fail("nonintegral graph depth")
        _rows[k] = row
        _ordered.append(k)

    # Reconstruct shortest path depth with actual native edges, without
    # granting pixels/lengths any physical meaning.
    var origin := _key(_source["origin"])
    if not _rows.has(origin):
        return _fail("missing declared origin")
    var reached: Dictionary = {origin: 0}
    var queue: Array = [origin]
    var cursor := 0
    while cursor < queue.size():
        var here: String = queue[cursor]
        cursor += 1
        for action in ["A", "B"]:
            var target: String = _key(_rows[here][action])
            if not _rows.has(target):
                return _fail("outgoing transition has no recorded destination")
            if not reached.has(target):
                reached[target] = int(reached[here]) + 1
                queue.append(target)
    if reached.size() != _rows.size() or queue != _ordered:
        return _fail("recorded state order differs from source BFS order")
    for k in _ordered:
        if int(_rows[k]["depth"]) != int(reached[k]):
            return _fail("recorded breadth-first depth differs from actual edges")

    var actions: Variant = _source.get("demo_actions")
    var trace: Variant = _source.get("demo_states")
    if not (actions is String) or actions.length() > 64 or not (trace is Array):
        return _fail("unbounded or missing native sample trace")
    if trace.size() != actions.length() + 1 or trace[0] != _source["origin"]:
        return _fail("sample trace has wrong endpoints")
    var sample: Array = _source["origin"]
    for i in range(actions.length()):
        var action: String = actions.substr(i, 1)
        if action != "A" and action != "B":
            return _fail("unknown native action in sample")
        sample = _rows[_key(sample)][action]
        if sample != trace[i + 1]:
            return _fail("sample sequence does not replay through native edges")
    _current = origin
    _inspected = origin
    return true


func _compute_layout() -> void:
    _positions.clear()
    if _rows.is_empty():
        return
    var levels: Dictionary = {}
    var last_depth := 0
    for key in _ordered:
        var d := int(_rows[key]["depth"])
        last_depth = max(last_depth, d)
        if not levels.has(d):
            levels[d] = []
        levels[d].append(key)
    var usable_width: float = max(400.0, size.x - 160.0)
    var usable_height: float = max(280.0, size.y - 280.0)
    for d in range(last_depth + 1):
        var group: Array = levels.get(d, [])
        for i in range(group.size()):
            var x: float = 80.0 + usable_width * float(d) / float(max(1, last_depth))
            var y: float = 145.0 + usable_height * float(i + 1) / float(group.size() + 1)
            _positions[group[i]] = Vector2(x, y)


func _draw_label(text: String, at: Vector2, size_px: int, tone: Color) -> void:
    var font := get_theme_default_font()
    if font != null:
        draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px, tone)


func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, size), BG)
    if not _error.is_empty():
        _draw_label("SOURCE DATA REFUSED: " + _error, Vector2(32, 60), 20, Color.RED)
        return
    if _rows.is_empty():
        _draw_label("No recorded finite states loaded", Vector2(32, 60), 18, MUTED)
        return

    _compute_layout()
    _draw_label("A/B  /  NATIVE FINITE MOTION", Vector2(32, 44), 25, Color.WHITE)
    _draw_label("F3^3  |  phi=(0,1,2)  |  27 source-derived states  |  54 A/B edges",
        Vector2(32, 72), 14, MUTED)
    _draw_label("A, B: advance   Backspace: revisit history   R: origin   P: play recorded sequence",
        Vector2(32, 102), 15, Color(0.78, 0.87, 0.94))
    _draw_label("Graph columns = shortest step counts. Screen positions and tweens are not physical geometry.",
        Vector2(32, size.y - 96), 13, MUTED)
    _draw_label("Finite example only; no universal A/B, collision, or worker-execution claim.",
        Vector2(32, size.y - 72), 13, MUTED)

    # Draw a complete directed transition topology. Lines are VIEW coordinates.
    for key in _ordered:
        var here: Vector2 = _positions[key]
        var row: Dictionary = _rows[key]
        for action in ["A", "B"]:
            var to_key: String = _key(row[action])
            var other: Vector2 = _positions[to_key]
            var col: Color = A_COLOR if action == "A" else B_COLOR
            col.a = 0.13
            if here.distance_to(other) < 1.0:
                draw_arc(here + Vector2(0.0, -18.0), 9.0, 0.0,
                    TAU, 20, col, 1.0, true)
            else:
                draw_line(here, other, col, 1.2, true)
    # Current outgoing movements can be seen independently before pressing.
    var position: Vector2 = _positions[_current]
    for action in ["A", "B"]:
        var target: Vector2 = _positions[_key(_rows[_current][action])]
        var col: Color = A_COLOR if action == "A" else B_COLOR
        draw_line(position, target, col, 3.5, true)

    # Past states/edges are path history, not an inverse asserted by Backspace.
    for change in _history:
        draw_line(_positions[change["from"]], _positions[change["to"]],
            Color(1.0, 0.79, 0.44, 0.78), 3.0, true)
    for key in _ordered:
        var at: Vector2 = _positions[key]
        var fill := MIDDLE
        if key == _inspected:
            fill = Color(0.28, 0.36, 0.47)
        if key == _current:
            fill = Color(0.16, 0.50, 0.54)
        draw_circle(at, 18.0, fill)
        draw_arc(at, 18.0, 0.0, TAU, 32, Color(0.48, 0.56, 0.67), 1.3, true)
        _draw_label(key.replace(",", ""), at + Vector2(-12.5, 4.7),
            12, Color.WHITE)

    var marker: Vector2 = _positions[_current]
    if _anim_time >= 0.0 and _positions.has(_anim_from) and _positions.has(_anim_to):
        var fraction: float = clamp(_anim_time / MOVE_SECONDS, 0.0, 1.0)
        marker = _positions[_anim_from].lerp(_positions[_anim_to], fraction)
    draw_circle(marker, 7.0, Color(1.0, 0.86, 0.42))
    var latest := "origin" if _history.is_empty() else str(_history[-1]["action"])
    _draw_label("Current: (" + _current + ")  |  last action: " + latest
        + "  |  actions: " + str(_history.size()),
        Vector2(32, size.y - 43), 17, Color.WHITE)
    _draw_label("Selected for inspection: (" + _inspected + ")",
        Vector2(max(32.0, size.x - 345.0), size.y - 43), 15, MUTED)


func _advance(action: String) -> void:
    if _rows.is_empty() or (action != "A" and action != "B"):
        return
    var former := _current
    var target: String = _key(_rows[former][action])
    _history.append({"from": former, "action": action, "to": target})
    _current = target
    _inspected = target
    _anim_from = former
    _anim_to = target
    _anim_time = 0.0
    queue_redraw()


func _process(delta: float) -> void:
    if _rows.is_empty():
        return
    if _anim_time >= 0.0:
        _anim_time += delta
        if _anim_time >= MOVE_SECONDS:
            _anim_time = -1.0
        queue_redraw()
    if _demo_playing and _anim_time < 0.0:
        if _demo_index >= _source["demo_actions"].length():
            _demo_playing = false
        else:
            _advance(_source["demo_actions"].substr(_demo_index, 1))
            _demo_index += 1


func _reset() -> void:
    _demo_playing = false
    _history.clear()
    _current = _key(_source["origin"])
    _inspected = _current
    _anim_time = -1.0
    queue_redraw()


func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    if _rows.is_empty():
        return
    match event.keycode:
        KEY_A:
            _demo_playing = false
            _advance("A")
        KEY_B:
            _demo_playing = false
            _advance("B")
        KEY_BACKSPACE:
            _demo_playing = false
            if not _history.is_empty():
                var last: Dictionary = _history.pop_back()
                _current = last["from"]
                _inspected = _current
                _anim_time = -1.0
                queue_redraw()
        KEY_R:
            _reset()
        KEY_P:
            _reset()
            _demo_index = 0
            _demo_playing = true
    get_viewport().set_input_as_handled()


func _gui_input(event: InputEvent) -> void:
    if (not (event is InputEventMouseButton) or not event.pressed
            or event.button_index != MOUSE_BUTTON_LEFT):
        return
    # A click only changes the INSPECTED state. It cannot teleport the model.
    for k in _positions:
        if _positions[k].distance_to(event.position) <= 18.0:
            _inspected = k
            queue_redraw()
            accept_event()
            return
