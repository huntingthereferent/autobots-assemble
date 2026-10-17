"""Find a witnessed convergence in the repository's native finite A/B world.

Do not pick a destination ahead of the trace. Follow source-native A and B,
verify each result independently, and only then show coincident endpoints.
This finite example is not a universal relationship among external feeds.
"""
from __future__ import annotations

from collections import deque
from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from work.arc_like_maze.math import World
from systems.workspace.ab_relational_cluster import _independent_step


def discover_convergence(max_states: int = 27) -> dict:
    if not 2 <= max_states <= 27:
        raise ValueError("invalid finite search budget")
    world = World(3, (0, 1, 2))
    paths = {"": world.origin}
    owners = {world.origin: ""}
    pending = deque([""])
    explored = 0
    while pending:
        word = pending.popleft()
        state = paths[word]
        explored += 1
        for action in "AB":
            target = world.step(state, action)
            if target != _independent_step(state, action):
                raise ValueError("native transition and independent verifier disagree")
            extended = word + action
            prior = owners.get(target)
            if prior is not None and prior != extended and prior and prior[0] != extended[0]:
                if world.apply(prior) != target or world.apply(extended) != target:
                    raise ValueError("native path replay disagrees")
                return {"schema": "finite-ab-convergence/v1",
                        "left_word": prior, "right_word": extended,
                        "target": list(target),
                        "initial": list(world.origin),
                        "states_explored": explored,
                        "source": "work/arc_like_maze/math.py",
                        "witness": "systems/workspace/ab_relational_cluster.py::_independent_step"}
            if prior is None and len(owners) < max_states:
                owners[target] = extended
                paths[extended] = target
                pending.append(extended)
    return {"schema": "finite-ab-convergence/v1", "status": "OPEN",
            "states_explored": explored,
            "source": "work/arc_like_maze/math.py"}


def animate(result: dict) -> str:
    if result.get("schema") != "finite-ab-convergence/v1":
        raise ValueError("not native finite source")
    if result.get("status") == "OPEN":
        raise ValueError("cannot draw a joined relation without an actual witness")
    left = result["left_word"]
    right = result["right_word"]
    state = "(" + ", ".join(map(str, result["target"])) + ")"
    e = lambda value: escape(str(value), quote=True)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="440" viewBox="0 0 1100 440" role="img" aria-labelledby="title desc">
<title id="title">A/B: actual convergence found by tracing</title>
<desc id="desc">In the finite F3 world, distinct source-verified action words {e(left)} and {e(right)} meet at {e(state)}. This is a mathematical example, not a claim of external or human convergence.</desc>
<style>
text{{font-family:ui-monospace,Consolas,monospace}}
.path{{stroke-dasharray:9 17;animation:movement 4s linear infinite}}
.path.slower{{animation-duration:6s;animation-delay:-2s}}
.focus{{animation:pulse 3.8s ease-in-out infinite;transform-origin:710px 242px}}
@keyframes movement{{to{{stroke-dashoffset:-156}}}}
@keyframes pulse{{50%{{opacity:.38;transform:scale(1.18)}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="1100" height="440" rx="16" fill="#080e19"/>
<rect x="12" y="12" width="1076" height="416" rx="12" fill="none" stroke="#31435c"/>
<text x="42" y="52" fill="#48d6eb" font-size="14" letter-spacing="2">NATIVE A/B · TRACE FIRST</text>
<text x="42" y="98" fill="#eef5ff" font-size="31">Two paths. One observed state.</text>
<text x="42" y="126" fill="#adbed4" font-size="14">Endpoints calculated from the original finite operators and independently checked</text>
<path d="M125 238L320 174Q435 174 545 238H699" fill="none" stroke="#48d6eb" stroke-opacity=".24" stroke-width="10"/>
<path d="M125 238L320 315Q435 315 545 238H699" fill="none" stroke="#8a83df" stroke-opacity=".24" stroke-width="10"/>
<path class="path" d="M125 238L320 174Q435 174 545 238H699" fill="none" stroke="#48d6eb" stroke-width="3"/>
<path class="path slower" d="M125 238L320 315Q435 315 545 238H699" fill="none" stroke="#8a83df" stroke-width="3"/>
<circle cx="125" cy="238" r="9" fill="#e1e9f2"/>
<circle class="focus" cx="710" cy="238" r="17" fill="#48d6eb" fill-opacity=".30" stroke="#48d6eb" stroke-width="2"/>
<circle cx="710" cy="238" r="5" fill="#48d6eb"/>
<text x="55" y="218" fill="#e1e9f2" font-size="15">origin (0,0,0)</text>
<text x="328" y="155" fill="#48d6eb" font-size="17">{e(left)}</text>
<text x="328" y="344" fill="#a59ae8" font-size="17">{e(right)}</text>
<text x="749" y="238" fill="#e8f0ff" font-size="23">{e(state)}</text>
<text x="749" y="264" fill="#a9bfd9" font-size="13">same source-verified endpoint</text>
<text x="43" y="388" fill="#a9bfd9" font-size="13">{e(result["states_explored"])} states expanded before this match · No path was chosen as a winner in advance</text>
<text x="43" y="410" fill="#7e9cb9" font-size="12">Scope: finite F3 world only · Source + independent replay in the repository</text>
</svg>'''
    ET.fromstring(svg)
    return svg


def main():
    result=discover_convergence()
    if result.get("status") == "OPEN":
        raise SystemExit("No valid convergence: do not publish a fake one")
    root=Path(__file__).resolve().parents[2]
    folder=root/"views/motion"
    (folder/"convergence-motion.svg").write_text(animate(result)+"\n",encoding="utf8")
    (folder/"convergence-receipt.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
