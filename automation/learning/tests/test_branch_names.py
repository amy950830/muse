import unittest

from automation.learning.branch_names import learning_branch, skill_branch


class BranchNamesTest(unittest.TestCase):
    def test_learning_branch_is_deterministic_and_safe(self):
        first = learning_branch("frontend", "2026-10-20", "React / Error Recovery!!!")
        second = learning_branch("frontend", "2026-10-20", "React / Error Recovery!!!")
        self.assertEqual(first, second)
        self.assertEqual(first, "learning/frontend/2026-10-20-react-error-recovery")
        self.assertNotIn(" ", first)
        self.assertNotIn("..", first)

    def test_skill_branch_uses_skill_namespace(self):
        self.assertEqual(
            skill_branch("backend-development", "2026-10-20", "API idempotency"),
            "evolution/backend-development/2026-10-20-api-idempotency",
        )

    def test_length_is_bounded(self):
        branch = learning_branch("security", "2026-10-20", "very-long-topic-" * 50)
        self.assertLessEqual(len(branch), 180)
        self.assertTrue(branch.startswith("learning/security/2026-10-20-"))

    def test_invalid_domain_or_skill_is_rejected(self):
        with self.assertRaises(ValueError):
            learning_branch("mobile", "2026-10-20", "topic")
        with self.assertRaises(ValueError):
            skill_branch("../../AGENTS.md", "2026-10-20", "topic")


if __name__ == "__main__":
    unittest.main()
