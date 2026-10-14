"""Run: python run_alternative_extension_demo.py"""
from ab_chatbot_alternative_extension import AlternativeExtensionChooser
from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN

# See test fixture for fully pinned bridge construction.
import test_ab_chatbot_path_union as fixture

if __name__=='__main__':
    test=fixture.PathUnionTests()
    discovered,*_=test.make((0,0,1),(1,0,1),depth=0,budget=54)
    selector=AlternativeExtensionChooser(PathUnionAgent(discovered,((0,0,0),)),((0,0,2),))
    for _ in range(250):
        result=selector.advance(max_new_edges_per_candidate=10)
        if result.status!='CONTINUING':break
    print(result.status, 'selected',result.selected_order)
    for a in result.alternatives:
        print(a.order,'states',a.state_pairs,'edges',a.admitted_edges,
              'goals',a.goals,'excluded',a.excluded_edges)
    print('possible images',result.possible_images)
