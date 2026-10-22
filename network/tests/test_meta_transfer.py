"""Transfer receipts cannot be inferred from workflow success or routing hints."""
import base64
import datetime as dt
import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote
from systems.workspace import meta_transfer as mt

A="huntingthereferent/autobots-assemble"
B="aeren-research/continuum-oscillator"
SHA="a"*40
WHEN="2026-10-22T18:30:00Z"
PAYLOAD=b'{"schema":"workstation-contract-probe-v1","no_research_payload":true}\n'
DIGEST=sha256(PAYLOAD).hexdigest()
SID="AB-20261022-CHECK-001"
SRC="state/transfers/payloads/contract-probe.json"
DST="state/transfers/payloads/contract-probe.json"


def record(state="DEPARTED"):
    r={"id":SID,"from":"A","to":"B","lane":"WORKSTATION",
       "status":state,"description":"source-owned transfer probe"}
    if state=="DEPARTED":
        r.update({"source_repo":A,"destination_repo":B,
                  "source_commit":SHA,"payload_sha256":DIGEST,
                  "source_payload_path":SRC,"destination_payload_path":DST,
                  "departed_at":WHEN})
    return r


def registry(path):
    path.write_text(json.dumps({"schema":"meta-workstation/registry-v1",
       "nodes":[{"id":"A","repo":A},{"id":"B","repo":B}]}))


def journal(row):
    return {"schema":"meta-workstation/handoffs-v1",
            "source_of_truth":A,"records":[row]}


def receiver(r, expect=True, ack=False):
    target={"schema":"meta-workstation/handoffs-v1",
            "source_of_truth":A,"records":[],"expectations":[],"received":[]}
    if expect:
        target["expectations"]=[{key:r[key] for key in
            ("id","from","to","lane","source_commit",
             "payload_sha256","destination_payload_path")}]
    if ack:
        target["received"]=[{"id":r["id"],"from":"A","to":"B",
                             "payload_sha256":r["payload_sha256"],
                             "source_commit":r["source_commit"],
                             "received_at":"2026-10-22T18:35:00Z"}]
    return target


def fake_getter(doc, destination_payload=None, source_payload=PAYLOAD):
    def get(path):
        if "/repos/"+B+"/contents/docs/live/meta-handoffs.json" in path:
            raw=json.dumps(doc).encode()
        elif "/repos/"+A+"/contents/"+SRC in path:
            raw=source_payload
        elif "/repos/"+B+"/contents/"+DST in path and destination_payload is not None:
            raw=destination_payload
        else:
            raise FileNotFoundError("Missing source-owned receipt")
        return {"encoding":"base64","content":base64.b64encode(raw).decode()}
    return get


class TransferReceiptTests(unittest.TestCase):
    def evaluate(self, row, getter):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/"registry.json"
            registry(f)
            return mt.observe(journal(row),f,getter=getter,
                              now=dt.datetime(2026,10,22,20,tzinfo=dt.timezone.utc))

    def test_blocked_departure_never_claims_sent_even_if_receiver_offline(self):
        def down(_):
            raise PermissionError("Destination account unavailable")
        r=self.evaluate(record("BLOCKED_PRE_DEPARTURE"),down)
        self.assertFalse(r["complete"])
        self.assertEqual(r["transfers"][0]["delivery"],"NOT_SENT")
        self.assertEqual(r["summary"]["verified"],0)
        self.assertTrue(r["summary"]["unverified_destination"])

    def test_departure_not_expected_is_visible_and_overdue(self):
        d=record()
        report=self.evaluate(d,fake_getter(receiver(d,expect=False)))
        self.assertTrue(report["complete"])
        item=report["transfers"][0]
        self.assertEqual(item["delivery"],"DEPARTED_NO_EXPECTATION")
        self.assertTrue(item["overdue"])

    def test_expected_but_not_arrived_does_not_fake_receipt(self):
        d=record()
        report=self.evaluate(d,fake_getter(receiver(d),destination_payload=None))
        self.assertEqual(report["transfers"][0]["delivery"],"EXPECTED_NOT_ARRIVED")

    def test_digest_and_missing_ack_are_distinct_failures(self):
        d=record()
        changed=self.evaluate(d,fake_getter(receiver(d),b"modified"))
        self.assertEqual(changed["transfers"][0]["delivery"],"DESTINATION_DIGEST_MISMATCH")
        arrived=self.evaluate(d,fake_getter(receiver(d),PAYLOAD))
        self.assertEqual(arrived["transfers"][0]["delivery"],"ARRIVED_UNACKNOWLEDGED")

    def test_ack_is_only_confirmed_when_content_matches_source(self):
        d=record()
        yes=self.evaluate(d,fake_getter(receiver(d,ack=True),PAYLOAD))
        self.assertTrue(yes["complete"])
        self.assertEqual(yes["transfers"][0]["delivery"],"RECEIVED_VERIFIED")
        self.assertEqual(yes["summary"]["verified"],1)
        self.assertFalse(yes["transfers"][0]["attention"])
        corrupted=self.evaluate(d,fake_getter(receiver(d,ack=True),PAYLOAD,b"bad source"))
        self.assertEqual(corrupted["transfers"][0]["delivery"],"SOURCE_DIGEST_MISMATCH")

    def test_ack_revision_mismatch_is_not_confirmed(self):
        d=record()
        r=receiver(d,ack=True)
        r["received"][0]["source_commit"]="b"*40
        result=self.evaluate(d,fake_getter(r,PAYLOAD))
        self.assertEqual(result["transfers"][0]["delivery"],"ACKNOWLEDGEMENT_MISMATCH")

    def test_orphan_incoming_expectation_is_observable(self):
        result=self.evaluate(record("BLOCKED_PRE_DEPARTURE"),
                              fake_getter(receiver(record())))
        self.assertTrue(any(t["delivery"]=="ORPHAN_EXPECTATION"
                            for t in result["transfers"]))

    def test_forged_source_or_path_refused(self):
        for key,bad in (("source_repo","another/repo"),
                        ("source_commit","main"),
                        ("source_payload_path","../secrets"),
                        ("payload_sha256","0"*20)):
            d=record()
            d[key]=bad
            with self.assertRaises(ValueError):
                mt.validate_departure(d,{"A":A,"B":B})


if __name__=="__main__":
    unittest.main()
