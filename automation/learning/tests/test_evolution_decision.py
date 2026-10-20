import unittest

from automation.learning.validate_evolution_decision import validate_evolution_decision


class EvolutionDecisionTest(unittest.TestCase):
    def base(self, level="L1"):
        return {
            "level": level,
            "confidence_score": 72,
            "reason": "Evidence supports a transferable improvement.",
            "sources": [{"repo": "example/project", "commit": "a" * 40}],
            "behavior_validation": "Not yet behavior-validated.",
            "protected_core_impact": False,
            "skill_candidate": None,
            "status": "SUPPORTED",
        }

    def test_l1_valid(self):
        self.assertEqual(validate_evolution_decision(self.base()), [])

    def test_l2_requires_threshold_validation_and_one_skill(self):
        data = self.base("L2")
        data.update({
            "confidence_score": 82,
            "behavior_validation": "Pressure scenario auth-idempotency passed before/after comparison.",
            "skill_candidate": {"target_skill": "backend-development", "proposal_path": "evolution/proposals/idempotency.md"},
        })
        self.assertEqual(validate_evolution_decision(data), [])

        for mutation in (
            {"confidence_score": 74},
            {"behavior_validation": ""},
            {"skill_candidate": None},
            {"skill_candidate": {"target_skill": "unknown-skill"}},
        ):
            invalid = dict(data)
            invalid.update(mutation)
            self.assertTrue(validate_evolution_decision(invalid))

    def test_l3_requires_human_review_and_no_auto_candidate(self):
        data = self.base("L3")
        data.update({
            "confidence_score": 95,
            "protected_core_impact": True,
            "status": "HUMAN_REVIEW_REQUIRED",
            "skill_candidate": None,
        })
        self.assertEqual(validate_evolution_decision(data), [])
        data["skill_candidate"] = {"target_skill": "application-security"}
        self.assertTrue(validate_evolution_decision(data))

    def test_protected_core_impact_forces_l3(self):
        data = self.base("L2")
        data.update({
            "confidence_score": 99,
            "protected_core_impact": True,
            "behavior_validation": "Validated",
            "skill_candidate": {"target_skill": "backend-development"},
        })
        errors = validate_evolution_decision(data)
        self.assertTrue(any("L3" in error for error in errors))

    def test_sources_are_mandatory(self):
        data = self.base()
        data["sources"] = []
        self.assertTrue(validate_evolution_decision(data))


if __name__ == "__main__":
    unittest.main()
