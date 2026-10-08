from __future__ import annotations

import unittest

from runtime.ab_loop import (
    ABAgent,
    ABFrame,
    ABLoop,
    ABMove,
    equivalent_for,
    render_agent_prompt,
)


class ABLoopTests(unittest.TestCase):
    def test_output_becomes_next_input_without_new_human_prompt(self):
        calls = []

        def worker(frame: ABFrame) -> ABMove:
            calls.append((frame.depth, frame.current["value"]))
            value = frame.current["value"]
            if value >= 3:
                return ABMove(
                    state="WALL",
                    reached={"value": value},
                    survived=frame.survives,
                    changed=(),
                    edge="target reached",
                    evidence=("value observed at target",),
                )
            return ABMove(
                state="MOVE",
                reached={"value": value + 1},
                survived=frame.survives,
                changed=(f"value:{value}->{value + 1}",),
                edge="compare next integer",
                evidence=("integer successor observed",),
            )

        initial = ABFrame(
            referent="integer successor",
            direction="follow +1",
            current={"value": 0},
            survives=("integer identity",),
            edge="compare next integer",
        )

        result = ABLoop((ABAgent("worker", worker),), max_steps=10).run(initial)

        self.assertEqual(calls[:4], [(0, 0), (1, 1), (2, 2), (3, 3)])
        self.assertEqual(result.move_count, 3)
        self.assertIn("all available agents", result.stop_reason)

    def test_wall_prompts_another_agent_and_success_restarts_loop(self):
        def increment_worker(frame: ABFrame) -> ABMove:
            if frame.current.get("reground"):
                return ABMove(
                    state="WALL",
                    reached=frame.current,
                    survived=frame.survives,
                    changed=(),
                    edge=frame.edge,
                    evidence=("increment worker has no relation across wall",),
                )

            value = frame.current["value"]
            if value < 2:
                return ABMove(
                    state="MOVE",
                    reached={"value": value + 1},
                    survived=frame.survives,
                    changed=(f"value:{value}->{value + 1}",),
                    edge="continue +1",
                    evidence=("successor relation",),
                )
            return ABMove(
                state="WALL",
                reached={"value": value, "new_relation": "double"},
                survived=frame.survives,
                changed=("successor relation no longer advances target",),
                edge="bridge +1 movement to x2 movement",
                evidence=("boundary exposes doubling relation",),
            )

        def bridge_worker(frame: ABFrame) -> ABMove:
            if frame.current.get("reground"):
                observation = frame.current.get("observation", {})
                if observation.get("new_relation") == "double":
                    value = observation["value"]
                    return ABMove(
                        state="MOVE",
                        reached={"value": value * 2, "mode": "double"},
                        survived=frame.survives,
                        changed=("direction:+1->x2", f"value:{value}->{value * 2}"),
                        edge="continue x2",
                        evidence=("doubling relation bridges wall",),
                        direction="follow x2",
                    )
                return ABMove(
                    state="WALL",
                    reached=frame.current,
                    survived=frame.survives,
                    changed=(),
                    edge=frame.edge,
                    evidence=("bridge worker found no supported bridge",),
                )

            value = frame.current["value"]
            if frame.direction == "follow x2" and value < 8:
                return ABMove(
                    state="MOVE",
                    reached={"value": value * 2, "mode": "double"},
                    survived=frame.survives,
                    changed=(f"value:{value}->{value * 2}",),
                    edge="continue x2",
                    evidence=("doubling relation",),
                )
            return ABMove(
                state="WALL",
                reached={"value": value},
                survived=frame.survives,
                changed=(),
                edge="target reached",
                evidence=("target boundary observed",),
            )

        initial = ABFrame(
            referent="numeric movement witness",
            direction="follow +1",
            current={"value": 0},
            survives=("numeric identity",),
            edge="continue +1",
        )

        result = ABLoop(
            (
                ABAgent("increment-worker", increment_worker),
                ABAgent("bridge-worker", bridge_worker),
            ),
            max_steps=12,
        ).run(initial)

        actors = [step.actor_id for step in result.steps]
        states = [step.move.state for step in result.steps]

        self.assertEqual(
            actors[:5],
            [
                "increment-worker",
                "increment-worker",
                "increment-worker",
                "bridge-worker",
                "bridge-worker",
            ],
        )
        self.assertEqual(states[:5], ["MOVE", "MOVE", "WALL", "MOVE", "MOVE"])
        self.assertTrue(result.steps[3].reground)
        self.assertEqual(result.steps[3].move.direction, "follow x2")
        self.assertEqual(result.steps[4].frame.current["value"], 4)
        self.assertEqual(result.steps[4].move.reached["value"], 8)
        self.assertGreaterEqual(result.reground_count, 1)
        self.assertIn("all available agents", result.stop_reason)

    def test_equivalence_is_conditional_on_history_sensitive_operations(self):
        shared = dict(
            referent="SK48 visible state",
            direction="continue forward-only movement",
            current={"active_y": 30, "visible_state": "same"},
            survives=("current board",),
            edge="next action",
        )
        history_a = ABFrame(
            **shared,
            provenance=("history:(1,2,1)", "rollback_depth:4"),
            depth=4,
        )
        history_b = ABFrame(
            **shared,
            provenance=("history:(2,2,1)", "rollback_depth:2"),
            depth=2,
        )

        self.assertTrue(
            equivalent_for(
                history_a,
                history_b,
                history_sensitive=False,
            )
        )
        self.assertFalse(
            equivalent_for(
                history_a,
                history_b,
                history_sensitive=True,
            )
        )

    def test_successful_move_can_change_referent_and_reground_direction(self):
        seen = []

        def worker(frame: ABFrame) -> ABMove:
            seen.append((frame.referent, frame.direction, frame.current["stage"]))
            if frame.current["stage"] == 0:
                return ABMove(
                    state="MOVE",
                    reached={"stage": 1},
                    survived=("provenance",),
                    changed=("level boundary crossed",),
                    edge="continue new referent",
                    evidence=("new returned state",),
                    referent="level-2 returned state",
                    direction="derive movement from returned state",
                )
            return ABMove(
                state="WALL",
                reached=frame.current,
                survived=frame.survives,
                changed=(),
                edge="witness complete",
                evidence=("boundary observed",),
            )

        initial = ABFrame(
            referent="level-1 state",
            direction="follow current relation",
            current={"stage": 0},
            survives=("provenance",),
            edge="cross level boundary",
        )

        result = ABLoop((ABAgent("worker", worker),), max_steps=4).run(initial)

        self.assertEqual(
            seen[:2],
            [
                ("level-1 state", "follow current relation", 0),
                (
                    "level-2 returned state",
                    "derive movement from returned state",
                    1,
                ),
            ],
        )
        self.assertIn("all available agents", result.stop_reason)

    def test_failed_reground_attempts_do_not_mutate_the_wall(self):
        wall_edges = []

        def first(frame: ABFrame) -> ABMove:
            if frame.current.get("reground"):
                wall_edges.append(("first", frame.edge, frame.current["observation"]))
                return ABMove(
                    state="WALL",
                    reached=frame.current,
                    survived=frame.survives,
                    changed=(),
                    edge=frame.edge,
                    evidence=("no bridge",),
                )
            return ABMove(
                state="WALL",
                reached={"split": ["left", "right"]},
                survived=("referent",),
                changed=("continuation split",),
                edge="choose supported continuation relation",
                evidence=("two continuations observed",),
            )

        def second(frame: ABFrame) -> ABMove:
            wall_edges.append(("second", frame.edge, frame.current["observation"]))
            return ABMove(
                state="WALL",
                reached=frame.current,
                survived=frame.survives,
                changed=(),
                edge=frame.edge,
                evidence=("also no bridge",),
            )

        initial = ABFrame(
            referent="ambiguous state",
            direction="continue",
            current={"stage": 0},
            survives=("referent",),
            edge="next",
        )

        result = ABLoop(
            (
                ABAgent("first", first),
                ABAgent("second", second),
            ),
            max_steps=5,
        ).run(initial)

        self.assertEqual(len(wall_edges), 1)
        self.assertEqual(
            wall_edges[0],
            (
                "second",
                "choose supported continuation relation",
                {"split": ["left", "right"]},
            ),
        )
        self.assertEqual(
            result.final_frame.current["observation"],
            {"split": ["left", "right"]},
        )
        self.assertEqual(
            result.final_frame.edge,
            "choose supported continuation relation",
        )

    def test_wall_or_unknown_swallow_first_and_resume_on_supported_move(self):
        seen = []

        def worker(frame: ABFrame) -> ABMove:
            seen.append(("worker", frame.current.get("stage")))
            if frame.current.get("stage") == "resumed":
                return ABMove(
                    state="MOVE",
                    reached={"stage": "continued"},
                    survived=frame.survives,
                    changed=("movement resumed",),
                    edge="next edge",
                    evidence=("post-swallow continuation",),
                )
            return ABMove(
                state="UNKNOWN",
                reached={"missing": "native source"},
                survived=frame.survives,
                changed=("known relation exhausted",),
                edge="find a native relation across the unknown",
                evidence=("current evidence insufficient",),
            )

        def swallower(frame: ABFrame) -> ABMove:
            seen.append(("swallow", frame.current.get("swallow")))
            return ABMove(
                state="MOVE",
                reached={"stage": "resumed", "source": "native witness"},
                survived=frame.survives,
                changed=("unknown -> native witness relation",),
                edge="continue with reached native witness",
                evidence=("native source inspected",),
                direction="follow reached native relation",
            )

        initial = ABFrame(
            referent="unknown boundary",
            direction="follow current relation",
            current={"stage": "start"},
            survives=("referent", "provenance"),
            edge="continue",
        )

        result = ABLoop(
            (ABAgent("worker", worker),),
            swallow_agent=ABAgent("swallow-worker", swallower),
            max_steps=3,
        ).run(initial)

        self.assertEqual(
            seen[:3],
            [
                ("worker", "start"),
                ("swallow", True),
                ("worker", "resumed"),
            ],
        )
        self.assertGreaterEqual(result.swallow_count, 1)
        self.assertGreaterEqual(result.move_count, 2)

    def test_failed_swallow_preserves_wall_before_other_agent_regrounds(self):
        observed = []

        def first(frame: ABFrame) -> ABMove:
            return ABMove(
                state="WALL",
                reached={"missing": "external relation"},
                survived=frame.survives,
                changed=("local path ended",),
                edge="missing external relation",
                evidence=("local evidence exhausted",),
            )

        def swallower(frame: ABFrame) -> ABMove:
            observed.append(("swallow", frame.edge, frame.current["observation"]))
            return ABMove(
                state="UNKNOWN",
                reached={"searched": True},
                survived=frame.survives,
                changed=(),
                edge=frame.edge,
                evidence=("no closing native witness found",),
            )

        def second(frame: ABFrame) -> ABMove:
            observed.append(
                (
                    "second",
                    frame.edge,
                    frame.current["observation"],
                    frame.current.get("swallow_attempted"),
                )
            )
            return ABMove(
                state="WALL",
                reached=frame.current,
                survived=frame.survives,
                changed=(),
                edge=frame.edge,
                evidence=("still unresolved",),
            )

        initial = ABFrame(
            referent="boundary",
            direction="continue",
            current={"stage": 0},
            survives=("referent",),
            edge="next",
        )

        result = ABLoop(
            (
                ABAgent("first", first),
                ABAgent("second", second),
            ),
            swallow_agent=ABAgent("swallow-worker", swallower),
            max_steps=4,
        ).run(initial)

        self.assertEqual(observed[0][0], "swallow")
        self.assertEqual(observed[1][0], "second")
        self.assertEqual(
            observed[0][2],
            {"missing": "external relation"},
        )
        self.assertEqual(
            observed[1][2],
            {"missing": "external relation"},
        )
        self.assertTrue(observed[1][3])
        self.assertTrue(result.final_frame.current["swallow_attempted"])

    def test_model_prompt_carries_shape_not_james_personality(self):
        frame = ABFrame(
            referent="catalog witness",
            direction="follow resource to direct evidence",
            current={"status": "catalog"},
            survives=("native fields", "provenance"),
            edge="is resource directly traversable?",
            walls=("do not invent geography",),
            provenance=("catalog:AU:weather",),
        )

        prompt = render_agent_prompt(frame)

        self.assertIn("REFERENT: catalog witness", prompt)
        self.assertIn("DIRECTION: follow resource to direct evidence", prompt)
        self.assertIn("SURVIVES:", prompt)
        self.assertIn("runtime will swallow outward first", prompt)
        self.assertNotIn("James", prompt)


if __name__ == "__main__":
    unittest.main()
