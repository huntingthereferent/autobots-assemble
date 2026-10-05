from __future__ import annotations


def normalize_text(text: str) -> dict:
    return {"normalized": " ".join(text.strip().lower().split())}


def word_count(normalized: str) -> dict:
    return {"count": len(normalized.split()) if normalized else 0}


def add(count: int, delta: int) -> dict:
    return {"count": count + delta}


def debounce(samples: list) -> dict:
    stable = False
    candidate = False
    run = 0
    toggles = 0
    led = False

    for raw in samples:
        pressed = bool(raw)
        if pressed != candidate:
            candidate = pressed
            run = 1
            continue

        run += 1
        if run == 3 and stable != candidate:
            stable = candidate
            if stable:
                led = not led
                toggles += 1

    return {
        "stable_pressed": stable,
        "led_on": led,
        "toggle_count": toggles,
    }


def describe_count(count: int) -> dict:
    parity = "even" if count % 2 == 0 else "odd"
    return {"description": f"{count} is {parity}"}
