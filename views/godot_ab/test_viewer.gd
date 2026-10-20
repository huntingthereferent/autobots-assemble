extends SceneTree
## Actually exercise the Godot-owned viewer against the admitted native data.
## No mock states, no physics engine and no worker execution.

func _initialize() -> void:
    call_deferred("_run")


func _check(condition: bool, message: String) -> bool:
    if not condition:
        push_error("A/B finite in-engine test failed: " + message)
        quit(3)
        return false
    return true


func _run() -> void:
    var packed: PackedScene = load("res://main.tscn")
    if packed == null:
        quit(3)
        return
    var viewer: Control = packed.instantiate()
    root.add_child(viewer)
    await process_frame
    if not _check(viewer._error == "", "viewer rejected native dataset"):
        return
    if not _check(viewer._rows.size() == 27, "not all 27 states were loaded"):
        return
    var start: String = viewer._current
    var actions: String = viewer._source["demo_actions"]
    var expected: Array = viewer._source["demo_states"]
    for i in range(actions.length()):
        viewer._advance(actions.substr(i, 1))
        if not _check(viewer._current == viewer._key(expected[i + 1]),
                      "action did not follow original declared edge"):
            return
        if not _check(viewer._history.size() == i + 1,
                      "navigation history lost a source step"):
            return
    viewer._reset()
    if not _check(viewer._current == start and viewer._history.is_empty(),
                  "reset did not return to selected finite origin"):
        return
    var key_a := InputEventKey.new()
    key_a.keycode = KEY_A
    key_a.pressed = true
    viewer._unhandled_key_input(key_a)
    if not _check(viewer._current == viewer._key(expected[1]),
                  "A key did not follow source edge"):
        return
    var rewind := InputEventKey.new()
    rewind.keycode = KEY_BACKSPACE
    rewind.pressed = true
    viewer._unhandled_key_input(rewind)
    if not _check(viewer._current == start and viewer._history.is_empty(),
                  "Backspace did not navigate its own recorded history"):
        return
    var autoplay := InputEventKey.new()
    autoplay.keycode = KEY_P
    autoplay.pressed = true
    viewer._unhandled_key_input(autoplay)
    if not _check(viewer._demo_playing and viewer._demo_index == 0,
                  "P key did not start bounded native demonstration"):
        return
    # No fake physics or ongoing worker behavior is required to test this.
    print("Verified Godot viewer: source-derived movements, keys, history and demo")
    quit(0)
