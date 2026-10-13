# 29 — Cross-invocation certificate handoff

[Detailed observed record](record.md) · [Integrated adapter](ab_chatbot_certificate_handoff.py) · [Owner-backed tests](test_ab_chatbot_certificate_handoff.py) · [Finite reference](finite_certificate_handoff.py) · [Finite tests](test_finite_certificate_handoff.py) · [Demo](run_certificate_handoff_demo.py) · [Result](CERTIFICATE_HANDOFF_RESULTS.json) · [Test accounting](CERTIFICATE_HANDOFF_REGRESSION.json)

The portable receipt requires fresh on-demand replay; SHA-256 is not owner authentication. The integrated adapter needs the complete separately archived Stage-20 owner-bound baseline. GitHub CI runs only the independent finite reference.
