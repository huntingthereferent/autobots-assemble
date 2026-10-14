"""Run an observable goal-completion example from bounded branch discovery."""
from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_goal_selected_restrictions import GoalSelectedRestrictions
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw


def demo() -> None:
    identity = tuple(DOMAIN)
    source = SourceOwnedHTTP(TransportedLaw((0, 0, 1), identity))
    changed = SourceOwnedHTTP(TransportedLaw((0, 0, 0), identity))
    with LoopbackHTTP(source) as s, LoopbackHTTP(changed) as t:
        old = LanguageBridge(RemoteObserver(s.url, bound_loopback=s),
                             owner=source, edge_budget=54)
        new = LanguageBridge(RemoteObserver(t.url, bound_loopback=t),
                             owner=changed, edge_budget=54)
        goal = (0, 1, 1)
        prior = GoalSelectedRestrictions(old, new, goal)
        while True:
            r = prior.advance(max_new_edges=4)
            if r.status != 'CONTINUING':
                break
        print('Two-strategy result:', r.status)
        branching = BranchDiscoverer(old, new, goal, max_depth=7)
        while True:
            r = branching.advance(max_new_edges=4)
            if r.status != 'CONTINUING':
                break
        print('New branch result:', r.status)
        print('Admitted path:', r.selected.word if r.selected else None)
        print('Old path:', r.selected.original_path.states if r.selected else None)
        print('Changed path:', r.selected.changed_path.states if r.selected else None)
        print('Candidate paths:', len(r.alternatives))
        print('Rejected attempted extensions:', len(r.rejected))
        print('Old/new unique observations:', r.old_observed_edges, r.new_observed_edges)
        if r.rejected:
            w = r.rejected[0].obstruction
            print('First rejected branch equality:', repr(w.left_word), repr(w.right_word))
            print('Equal endpoints old/new:', w.old_equal, w.new_equal)


if __name__ == '__main__':
    demo()
