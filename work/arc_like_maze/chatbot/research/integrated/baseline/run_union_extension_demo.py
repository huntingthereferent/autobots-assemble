"""Local, owned finite-law demonstration of missing-edge investigation."""
from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_union_extension import UnionEdgeExtender
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw


def owned_bridge(phi, connection_stack):
    owner = SourceOwnedHTTP(TransportedLaw(phi, tuple(DOMAIN)))
    server = connection_stack.enter_context(LoopbackHTTP(owner))
    return LanguageBridge(RemoteObserver(server.url, bound_loopback=server),
                          owner=owner, edge_budget=54)


def run(phi_old, phi_new, *, starting_depth=0):
    from contextlib import ExitStack
    with ExitStack() as stack:
        old = owned_bridge(phi_old, stack)
        new = owned_bridge(phi_new, stack)
        branch = BranchDiscoverer(old, new, (0,0,0), max_depth=starting_depth)
        while True:
            status = branch.advance(max_new_edges=6)
            if status.status != 'CONTINUING':
                break
        source = PathUnionAgent(branch, ((0,0,0),))
        initial = source.run()
        extender = UnionEdgeExtender(source)
        for _ in range(250):
            report = extender.advance(max_new_edges=3)
            if report.status != 'CONTINUING':
                break
        else:
            raise RuntimeError('extension never completed inside local bound')
        print('old',phi_old,'changed',phi_new)
        print('initial:', len(initial.selected.state_pairs),'state pairs;',
              len(initial.selected.admitted_edges),'admitted edges')
        print('final:', report.status)
        print('state pairs:',len(report.state_pairs),'admitted edges:',
              len(report.admitted_edges),'new edges:',len(report.new_edges))
        print('excluded:',len(report.rejected),'unique observations:',
              report.old_observed_edges,report.new_observed_edges)
        for edge in report.rejected:
            r=edge.witness
            print(' excluded',edge.source,edge.action,edge.cause,
                  repr(r.left_word),'vs',repr(r.right_word),
                  'old_equal',r.old_equal,'changed_equal',r.new_equal)
        print()


if __name__ == '__main__':
    run((0,0,1),(0,0,0))
    run((0,0,1),(0,0,1))
