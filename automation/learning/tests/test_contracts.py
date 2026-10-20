import unittest

from automation.learning import contracts


class ContractsTest(unittest.TestCase):
    def test_core_contract_constants(self):
        self.assertEqual(contracts.ALLOWED_DOMAINS, ("frontend", "backend", "security"))
        self.assertEqual(contracts.CANDIDATE_TRACKS, ("stable", "emerging"))
        self.assertEqual(contracts.EVOLUTION_LEVELS, ("L0", "L1", "L2", "L3"))
        self.assertEqual(contracts.CONFIDENCE_VALUES, ("High", "Medium", "Exploratory"))
        self.assertEqual(contracts.ORDINARY_AUTO_WRITE_ROOTS, ("knowledge/", "evolution/"))

    def test_protected_paths_cover_governance_and_automation(self):
        protected = set(contracts.PROTECTED_PATHS)
        for expected in (
            "IDENTITY.md",
            "AGENTS.md",
            "SKILLS.md",
            ".agents/",
            ".github/",
            "automation/",
        ):
            self.assertIn(expected, protected)


if __name__ == "__main__":
    unittest.main()
