"""Live local-owner demo of a selected commuting square across distinct pin scopes."""
import json
from pathlib import Path
from dataclasses import asdict
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer
from test_ab_chatbot_cross_scope_transport import CrossScopeTransportTests

def main():
    f=CrossScopeTransportTests()
    try:
        recipient,donor,*_=f.fixture()
        before=(len(recipient.old.snapshot.edges),len(recipient.new.snapshot.edges),
                len(donor.old.snapshot.edges),len(donor.new.snapshot.edges))
        req=f.declaration(recipient,donor)
        positive=CrossScopeIntertwiningTransfer(recipient,donor,req).advance()
        assert positive.status=='CROSS_SCOPE_INTERTWINING_WITNESSED'
        after=(len(recipient.old.snapshot.edges),len(recipient.new.snapshot.edges),
                len(donor.old.snapshot.edges),len(donor.new.snapshot.edges))
        bad=f.declaration(recipient,donor)
        bad['new_state_transport'][1]['recipient']=[1,2,1]
        negative=CrossScopeIntertwiningTransfer(recipient,donor,bad).advance()
        assert negative.status=='TRANSPORT_INTERTWINING_CONFLICT'
        data={'scope':'different owner objects, separate registries, four separately pinned snapshots',
              'recipient_laws':[(0,0,0),(0,1,2)],
              'donor_laws':[(0,0,1),(1,0,1)],
              'selected_donor_edge':[(1,0,0),'B'],
              'declared_old_transport':req['old_state_transport'],
              'declared_new_transport':req['new_state_transport'],
              'observations_before':before,'observations_after':after,
              'new_recipient_observations':[after[0]-before[0],after[1]-before[1]],
              'new_donor_observations':[after[2]-before[2],after[3]-before[3]],
              'success':{'status':positive.status,'paired_states':len(positive.state_pairs),
                         'admitted_edges':len(positive.admitted_edges),
                         'selected_square':positive.selected_square,
                         'derived_fingerprint':positive.derived_fingerprint},
              'negative':{'status':negative.status,'obstruction':negative.obstruction},
              'source_claim_limit':'local in-process verified owner binding; no remote authentication or whole-system equivalence'}
        print(json.dumps(data,indent=2))
        Path(__file__).with_name('CROSS_SCOPE_TRANSPORT_RESULTS.json').write_text(json.dumps(data,indent=2)+'\n')
    finally:f.doCleanups()

if __name__=='__main__':main()
