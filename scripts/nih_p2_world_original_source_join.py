"""Verify real owner-attributed AACT evidence stays separate from the W13 game."""
import json
from pathlib import Path
import sys

def check(owner,game):
    if (owner.get("schema")!="nih-p2-2022-aact-owner-script-date-reference/v1"
        or owner.get("original_source_owner")!="lalagkaspn/mendelian_comorbidity_therapeutics"
        or owner.get("original_source_2022_date_owner_attested")!="2022-11-04"
        or owner.get("earlier_author_commit")!="96ccb828b5118e54c658fc1cd386173de67a4b4"
        or owner.get("linked_author_commit")!="675b7a4992d7e2469d368924f4c1f87d7ca162da"
        or owner.get("earlier_source_witness",{}).get("git_blob_sha1")!="3a5781267f15fa69ae1779e47cdb0b4e1f1f0cb6"
        or owner.get("linked_source_witness",{}).get("git_blob_sha1")!="3e3f8714df2c037cce24961a57802546ce95f7b4"
        or owner.get("owner_attested_source_date") is not True
        or owner.get("2022_download_transaction_independently_timestamped") is not False
        or owner.get("individual_registry_version_publication_instants_authenticated") is not False
        or game.get("schema")!="world-nih-p2-synthetic-source-event-chronology/v1"
        or game.get("original_native_jobs")!=12 or game.get("source_event_count")!=3
        or game.get("source_events_are_constructed_not_authenticated") is not True
        or game.get("source_signature_authenticated") is not False
        or game.get("original_native_journals_unchanged") is not True):
        raise ValueError("source owner identity or independent temporal boundary not supported")
    return {"schema":"world-nih-p2-authenticated-source-reference-boundary/v1",
        "pinned_git_source_file_blobs_verified":True,
        "source_owner_attests_AACT_collection_date":"2022-11-04",
        "source_owner_statement_not_independent_2022_download_capture":True,
        "historical_registry_version_timestamp_verified":False,
        "source_owner_statement_joined_to_fictional_game_events":False,
        "synthetic_W13_events":3,"retained_native_jobs":12,
        "native_journal_changed":False,"official_NIH_submission":False}

if __name__=="__main__":
    owner=json.loads(Path(sys.argv[1]).read_text())
    game=json.loads(Path(sys.argv[2]).read_text())
    result=check(owner,game)
    Path(sys.argv[3]).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
