import unittest

from automation.learning.resolve_run import resolve_domain
from automation.learning.validate_research_plan import validate_research_plan


class ResolveRunTest(unittest.TestCase):
    def test_scheduled_domain_mapping(self):
        self.assertEqual(resolve_domain("schedule", "0 3 * * 1", None), "frontend")
        self.assertEqual(resolve_domain("schedule", "0 3 * * 3", None), "backend")
        self.assertEqual(resolve_domain("schedule", "0 3 * * 5", None), "security")

    def test_manual_dispatch_requires_allowed_domain(self):
        self.assertEqual(resolve_domain("workflow_dispatch", None, "backend"), "backend")
        with self.assertRaises(ValueError):
            resolve_domain("workflow_dispatch", None, "mobile")
        with self.assertRaises(ValueError):
            resolve_domain("workflow_dispatch", None, None)

    def test_unknown_schedule_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_domain("schedule", "0 3 * * 2", None)


class ResearchPlanValidationTest(unittest.TestCase):
    def valid_plan(self):
        return {
            "domain": "frontend",
            "topic": "resilient-ui-error-recovery",
            "reason": "Existing coverage is stale and recent evidence is relevant.",
            "priority_score": 86,
            "knowledge_gap": "HIGH",
            "freshness_risk": "MEDIUM",
            "trend_signal": "HIGH",
            "research_questions": ["Which recovery patterns transfer across frameworks?"],
            "candidate_tracks": ["stable", "emerging"],
        }

    def test_valid_plan_passes(self):
        self.assertEqual(validate_research_plan(self.valid_plan(), "frontend"), [])

    def test_required_fields_and_ranges_are_enforced(self):
        plan = self.valid_plan()
        plan["domain"] = "backend"
        plan["topic"] = "Not A Slug!"
        plan["priority_score"] = 101
        plan["reason"] = ""
        plan["knowledge_gap"] = "EXTREME"
        plan["research_questions"] = []
        errors = validate_research_plan(plan, "frontend")
        self.assertGreaterEqual(len(errors), 6)

    def test_both_tracks_required_without_niche_exception(self):
        plan = self.valid_plan()
        plan["candidate_tracks"] = ["stable"]
        self.assertTrue(validate_research_plan(plan, "frontend"))
        plan["niche_topic_exception"] = "Only one mature implementation exists for this narrow protocol."
        self.assertEqual(validate_research_plan(plan, "frontend"), [])


if __name__ == "__main__":
    unittest.main()
