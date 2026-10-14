"""Reproduce the path-union and incompatible-union experiments locally."""
from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw


def main():
    identity = tuple(DOMAIN)
    original = SourceOwnedHTTP(TransportedLaw((0, 0, 1), identity))
    changed = SourceOwnedHTTP(TransportedLaw((0, 0, 0), identity))
    with LoopbackHTTP(original) as s, LoopbackHTTP(changed) as t:
        a = LanguageBridge(RemoteObserver(s.url, bound_loopback=s),
                           owner=original, edge_budget=54)
        b = LanguageBridge(RemoteObserver(t.url, bound_loopback=t),
                           owner=changed, edge_budget=54)
        discovery = BranchDiscoverer(a, b, (0,1,1), max_depth=7)
        while True:
            observed = discovery.advance(max_new_edges=5)
            if observed.status != 'CONTINUING':
                break
        print('Discovery:', observed.status,
              'prefixes:', len(discovery.prefixes), 'rejections:', len(observed.rejected))
        print('\nTwo compatible target paths:')
        joined = PathUnionAgent(discovery, ((0,1,1),(2,2,0)),
                                variants_per_goal=1).run()
        print('  status:', joined.status)
        print('  candidate words:', joined.candidate_words)
        print('  accepted words:', joined.selected.words)
        print('  joint state pairs:', len(joined.selected.state_pairs))
        print('  distinct admitted edges:', len(joined.selected.admitted_edges))
        print('  transported goals:', joined.selected.carried_goals)
        print('\nTwo individually valid, jointly incompatible paths:')
        blocked = PathUnionAgent(discovery, ((0,1,1),(0,1,0)),
                                 variants_per_goal=1).run()
        print('  status:', blocked.status)
        print('  candidate words:', blocked.candidate_words)
        print('  carried:', blocked.selected.carried_goals)
        for conflict in blocked.conflicts:
            w = conflict.witness
            print('  incompatible words:', conflict.left_candidate, conflict.right_candidate)
            print('  separating relation:', repr(w.left_word), repr(w.right_word))
            print('  endpoint equality old/new:', w.old_equal, w.new_equal)
        print('\nUnique old/new edge reads:', len(a.snapshot.edges), len(b.snapshot.edges))
        print('No global equivalence or unexamined-edge closure is claimed.')


if __name__ == '__main__':
    main()
