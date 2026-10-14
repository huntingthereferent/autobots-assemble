"""Demonstrate replacement by fresh local owner pins and observations."""
import json
from pathlib import Path
from test_ab_chatbot_source_replacement_recovery import SourceReplacementRecoveryTests


def run_case(agreeing):
    fixture=SourceReplacementRecoveryTests('test_agreeing_replacement_creates_new_agreement')
    try:
        recover,history,comparison,left,right,oldmiddle,registry,token,newmiddle,newregistry,p,q=fixture.fixture(agreeing=agreeing)
        before=recover._counts()
        report=recover.advance()
        after=recover._counts()
        repeated=recover.advance()
        return {
            'replacement': 'matching-route' if agreeing else 'conflicting-route',
            'original_historical_status':report.historical.status,
            'old_right_pin_revoked':not registry.verify(token.token,oldmiddle.new),
            'old_route_after_change':report.historical_refresh.right_route,
            'unaffected_left_route':report.historical_refresh.left_route,
            'recovery_status':report.status,
            'new_comparison':report.recovered_comparison.status if report.recovered_comparison else None,
            'new_right_witness_fingerprint': report.replacement.fingerprint if report.replacement else None,
            'new_right_pairs':len(report.replacement.state_pairs) if report.replacement else 0,
            'new_right_edges':len(report.replacement.admitted_edges) if report.replacement else 0,
            'counts_before_recovery':before,
            'counts_after_recovery':after,
            'comparison_revisit_status':repeated.status,
            'counts_after_revisit':recover._counts(),
            'replacement_registry_new':newregistry is not oldmiddle.registry,
            'replacement_owner_sources_new':newmiddle.old is not oldmiddle.old and newmiddle.new is not oldmiddle.new,
            'historical_current_is_separate':report.historical is not report.recovered_comparison,
        }
    finally:
        fixture.doCleanups()


def main():
    data={'scope':'two independent locally owner-pinned source pairs; on-demand recovery',
          'cases':[run_case(True),run_case(False)],
          'limits':['not remote identity authentication','not automatic source monitoring',
                    'not global source correspondence','historical route evidence not transferred']}
    path=Path(__file__).with_name('SOURCE_REPLACEMENT_RECOVERY_RESULTS.json')
    path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__=='__main__':main()
