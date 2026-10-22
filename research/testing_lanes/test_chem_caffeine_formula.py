"""Offline controls for CHEM-CAFFEINE-FORMULA-001."""
import unittest

from chem_caffeine_formula import formula_mass, validate_properties, CID


class ChemCaffeineTests(unittest.TestCase):
    def fixture(self):
        return {
            "CID": CID,
            "MolecularFormula": "C8H10N4O2",
            "MolecularWeight": 194.19,
            "CanonicalSMILES": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
        }

    def test_formula_mass_matches_reported_value_within_tolerance(self):
        result = validate_properties(self.fixture())
        self.assertEqual(result["outcome"], "FORMULA_MASS_CONSISTENT")
        self.assertLessEqual(result["absolute_mass_difference_g_mol"], 0.05)

    def test_known_formula_mass(self):
        self.assertAlmostEqual(formula_mass("C8H10N4O2"), 194.194, places=6)

    def test_rejects_wrong_compound_identity(self):
        data = self.fixture()
        data["CID"] = 999
        with self.assertRaises(ValueError):
            validate_properties(data)

    def test_rejects_wrong_formula(self):
        data = self.fixture()
        data["MolecularFormula"] = "C8H10N4"
        with self.assertRaises(ValueError):
            validate_properties(data)

    def test_rejects_mass_mismatch(self):
        data = self.fixture()
        data["MolecularWeight"] = 250.0
        with self.assertRaises(ValueError):
            validate_properties(data)

    def test_rejects_unsupported_or_malformed_formula(self):
        with self.assertRaises(ValueError):
            formula_mass("C8H10N4O2?")
        with self.assertRaises(ValueError):
            formula_mass("C2Cl")
        

if __name__ == "__main__":
    unittest.main()
