"""Preserve full marked A/B witnesses through stemmed gauges and mixed words."""
import unittest
from itertools import product

from work.arc_like_maze.root_transport import (
    Process, Witness, verify, ZERO, IDENTITY, NEGATIVE, verify_marked_pair,
)
from work.arc_like_maze.marked_operator_system import (
    MarkedArrow, MarkedObject, same_arrow, shift_arrow, compose_arrows,
    identical_streams,
)
from work.arc_like_maze.stemmed_operator_system import (
    StemGauge, same_gauge, gauge_arrow, interchange_stem, audit_stemmed,
    GaugeStep, ShiftStep, normalize_word, execute_word, certify_word,
)


class StemmedOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = Process((ZERO, (0,0,1)), ((0,0,1), ZERO))
        cls.bridge = StemGauge(2, (2,), (1,2))
        cls.q = cls.bridge.apply(cls.p)
        cls.arrow = MarkedArrow(MarkedObject(cls.p,1),MarkedObject(cls.q,2),
                                Witness('ALIGNED',2,(2,),(1,2)))

    def test_exact_audit(self):
        cert = audit_stemmed()
        self.assertEqual(cert.status,'CLOSED_STEM_GAUGE_INTERCHANGE')
        self.assertEqual((cert.gauges,cert.process_templates),(12,81))
        self.assertEqual((cert.compositions_checked,cert.gauge_shift_squares),(11664,864))
        self.assertEqual(cert.counterexamples,1)

    def test_stemmed_coordinate_action_and_inverse(self):
        gauges=(StemGauge(2,(2,1),(1,2)),StemGauge(1,(1,2,2),(2,1)),
                StemGauge.periodic(2,2,1))
        processes=(self.p,Process.repeat(IDENTITY,NEGATIVE),
                   Process((IDENTITY,ZERO),(NEGATIVE,IDENTITY)))
        for g in gauges:
            for p in processes:
                q=g.apply(p)
                w=Witness('ALIGNED',g.incoming,g.stem,g.period)
                self.assertTrue(verify(p,q,w))
                a=MarkedArrow(MarkedObject(p,1),MarkedObject(q,g.incoming),w)
                for depth in (3,4,5,6):
                    self.assertTrue(verify_marked_pair(a.source.world(),a.target.world(),w,depth))
                double=g.compose(g.inverse())
                self.assertTrue(same_gauge(double,StemGauge.periodic(1,1)))
                self.assertTrue(identical_streams(double.apply(p),p))

    def test_composition_and_shifts_extend_finite_stems(self):
        gauges=(StemGauge(2,(2,1),(1,2,2)),StemGauge(1,(1,2,2,1),(2,)),
                StemGauge.periodic(2,2,1),StemGauge(1,(),(2,1,1)))
        for u,v in product(gauges,repeat=2):
            self.assertTrue(identical_streams(u.apply(v.apply(self.p)),u.compose(v).apply(self.p)))
            for k,l in ((0,0),(1,1),(2,4),(3,2),(6,7)):
                self.assertTrue(same_gauge(u.shifted(k).shifted(l),u.shifted(k+l)))
                self.assertTrue(same_gauge(u.compose(v).shifted(k),
                                           u.shifted(k).compose(v.shifted(k))))
                self.assertTrue(interchange_stem(self.arrow,u,v,k))

    def test_arbitrary_source_target_gauge_stems_preserve_marked_arrows(self):
        u=StemGauge(2,(2,2,1),(1,2));v=StemGauge(2,(1,2),(2,1,1))
        transformed=gauge_arrow(self.arrow,u,v)
        for depth in (3,4,5,6,7):
            self.assertTrue(verify_marked_pair(transformed.source.world(),
                                               transformed.target.world(),
                                               transformed.witness,depth))
        for k in range(0,15):
            self.assertTrue(interchange_stem(self.arrow,u,v,k))

    def test_witness_choice_not_recomputed_after_shift(self):
        p=Process.repeat(ZERO)
        w=Witness('ALIGNED',2,(1,2,1,2),(2,1,1))
        original=MarkedArrow(MarkedObject(p,1),MarkedObject(p,2),w)
        u=StemGauge(2,(1,2),(1,2))
        v=StemGauge(1,(2,1,1),(1,))
        for k in range(0,10):
            self.assertTrue(interchange_stem(original,u,v,k))
            t=shift_arrow(original,k)
            self.assertEqual(t.witness.incoming,w.incoming if k==0 else w.scale(k-1))
            for i in range(12):self.assertEqual(t.witness.scale(i),w.scale(k+i))

    def test_word_normalization_for_mixed_sequences(self):
        u=StemGauge(2,(2,1),(1,2))
        v=StemGauge(1,(1,2,2),(2,1))
        w=StemGauge(2,(1,2,1,2),(1,))
        instructions=(GaugeStep(u,v),ShiftStep(1),GaugeStep(w,u),
                      ShiftStep(3),GaugeStep(v,w),ShiftStep(4),
                      GaugeStep(u,w))
        self.assertTrue(certify_word(self.arrow,instructions))
        normal=normalize_word(instructions)
        self.assertEqual(normal.removed_rules,8)
        self.assertTrue(same_arrow(execute_word(self.arrow,instructions),normal.act(self.arrow)))
        for depth in range(3,7):
            out=normal.act(self.arrow)
            self.assertTrue(verify_marked_pair(out.source.world(),out.target.world(),
                                               out.witness,depth))

    def test_all_short_mixed_words_have_a_correct_normal_form(self):
        g=GaugeStep(StemGauge(2,(1,2),(2,1)),StemGauge(1,(2,),(1,2)))
        h=GaugeStep(StemGauge(1,(2,1,2),(2,)),StemGauge(2,(1,2),(1,)))
        choices=(g,h,ShiftStep(1),ShiftStep(2))
        count=0
        for length in (1,2,3,4):
            for sequence in product(choices,repeat=length):
                self.assertTrue(certify_word(self.arrow,sequence))
                count+=1
        self.assertEqual(count,4+16+64+256)

    def test_noninvertible_shift_remains_explicit(self):
        p=Process((ZERO,IDENTITY),(NEGATIVE,))
        self.assertNotEqual(p,p.shift(1))
        self.assertNotEqual(p,p.shift(2))
        # Once the prefix is discarded, applying any nonnegative further
        # shift cannot recover it as the initial process sequence.
        self.assertFalse(any(identical_streams(p,p.shift(2).shift(k)) for k in range(15)))
        word=normalize_word((ShiftStep(2),))
        self.assertEqual(word.removed_rules,2)

    def test_invalid_marks_and_operator_words(self):
        for incoming,stem,period in ((0,(),(1,)),(1,(0,),(1,)),(1,(),()),
                                      (1,(True,),(1,))):
            with self.assertRaises(ValueError):StemGauge(incoming,stem,period)
        with self.assertRaises(ValueError):StemGauge.periodic(1,1).shifted(-1)
        with self.assertRaises(ValueError):ShiftStep(-1)
        with self.assertRaises(TypeError):normalize_word(('not an admitted operator',))


if __name__=='__main__':unittest.main(verbosity=2)
