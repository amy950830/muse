import unittest

from automation.learning.validate_learning_output import validate_changed_paths


class OutputGuardTest(unittest.TestCase):
    def test_allows_only_knowledge_and_evolution(self):
        allowed = [
            "knowledge/frontend/example.md",
            "evolution/proposals/example.md",
            "evolution/evaluations/example.md",
            "evolution/changelog.md",
        ]
        self.assertEqual(validate_changed_paths(allowed), [])

    def test_rejects_governance_automation_and_unrelated_files(self):
        rejected = [
            ".agents/skills/backend-development/SKILL.md",
            "AGENTS.md",
            "IDENTITY.md",
            "SKILLS.md",
            ".github/workflows/muse-learning.yml",
            "automation/learning/scoring.py",
            "README.md",
        ]
        errors = validate_changed_paths(rejected)
        self.assertEqual(len(errors), len(rejected))

    def test_rejects_path_traversal_and_absolute_paths(self):
        errors = validate_changed_paths([
            "knowledge/../AGENTS.md",
            "/tmp/evolution/proposals/evil.md",
            "knowledge\\..\\AGENTS.md",
        ])
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
