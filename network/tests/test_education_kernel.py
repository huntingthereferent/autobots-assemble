from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.education import EducationKernel, Observation


class EducationKernelTests(unittest.TestCase):
    def test_present_evidence_regrounds_without_erasing_prior_relation(self):
        kernel=EducationKernel()
        first=kernel.observe(Observation.create(
            person_ref="learner-x",
            referent="addition-across-ten",
            observed="counted every item",
            supports=("count-all available",),
            evidence_refs=("work:1",),
        ))
        second=kernel.observe(Observation.create(
            person_ref="learner-x",
            referent="addition-across-ten",
            observed="made ten independently",
            supports=("make-ten available",),
            contradicts=("count-all available",),
            evidence_refs=("work:2",),
        ))
        self.assertEqual(kernel.current("learner-x","addition-across-ten"),second)
        self.assertIn("make-ten available",second.supported)
        self.assertIn("count-all available",second.unsupported)
        self.assertEqual(second.supersedes,first.relation_id)
        self.assertEqual(kernel.relation(first.relation_id),first)
        self.assertIn(f"education-relation:{first.relation_id}",second.provenance)

    def test_different_referents_for_same_person_do_not_flatten(self):
        kernel=EducationKernel()
        math=kernel.observe(Observation.create(
            person_ref="learner-x", referent="fractions",
            observed="identified halves", supports=("halves recognized",)))
        reading=kernel.observe(Observation.create(
            person_ref="learner-x", referent="decoding",
            observed="decoded short vowel word", supports=("cvc decoding available",)))
        self.assertEqual(kernel.current("learner-x","fractions"),math)
        self.assertEqual(kernel.current("learner-x","decoding"),reading)

    def test_append_only_recovery_preserves_front_and_back(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"education.jsonl"
            kernel=EducationKernel(path)
            first=kernel.observe(Observation.create(
                person_ref="p",referent="r",observed="first",supports=("A",)))
            second=kernel.observe(Observation.create(
                person_ref="p",referent="r",observed="second",
                supports=("B",),contradicts=("A",)))
            recovered=EducationKernel(path)
            self.assertEqual(recovered.current("p","r").relation_id,second.relation_id)
            self.assertEqual(recovered.relation(first.relation_id).supported,("A",))
            self.assertEqual(len(recovered.events()),4)


if __name__=="__main__":
    unittest.main()
