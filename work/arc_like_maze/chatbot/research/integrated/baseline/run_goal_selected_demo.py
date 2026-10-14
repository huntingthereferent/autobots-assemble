"""Locally run the goal-sensitive finite A/B restriction chooser."""
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_goal_selected_restrictions import GoalSelectedRestrictions
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_stability_witness import TransportedLaw


def demo() -> None:
    identity = tuple(DOMAIN)
    owner_old = SourceOwnedHTTP(TransportedLaw((0, 0, 1), identity))
    owner_new = SourceOwnedHTTP(TransportedLaw((0, 0, 0), identity))
    with LoopbackHTTP(owner_old) as a, LoopbackHTTP(owner_new) as b:
        old = LanguageBridge(RemoteObserver(a.url, bound_loopback=a),
                             owner=owner_old, edge_budget=54)
        new = LanguageBridge(RemoteObserver(b.url, bound_loopback=b),
                             owner=owner_new, edge_budget=54)
        for goal in ((1, 1, 1), (1, 1, 0)):
            chooser = GoalSelectedRestrictions(old, new, goal)
            for _ in range(300):
                report = chooser.advance(max_new_edges=3)
                if report.status != 'CONTINUING':
                    break
            else:
                raise RuntimeError('iteration limit reached without a terminal report')
            print('Goal:', goal)
            print('Status:', report.status)
            print('Selected:', report.selected_strategy)
            print('Path:', report.original_path.word if report.original_path else None)
            print('Image:', report.target_image)
            print('Alternatives:', [(c.strategy, c.goal_status, c.target_image)
                                     for c in report.candidates])
            print('Unique observations:', report.old_observed_edges,
                  report.new_observed_edges)
            print()


if __name__ == '__main__':
    demo()
