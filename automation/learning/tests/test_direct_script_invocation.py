import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DIRECT_SCRIPTS = (
    "automation/learning/resolve_run.py",
    "automation/learning/secret_guard.py",
    "automation/learning/validate_research_plan.py",
    "automation/learning/collect_github_research.py",
    "automation/learning/validate_evolution_decision.py",
    "automation/learning/validate_learning_output.py",
    "automation/learning/validate_skill_candidate.py",
)


class DirectScriptInvocationTest(unittest.TestCase):
    def test_workflow_helpers_can_start_when_invoked_by_file_path(self):
        for script in DIRECT_SCRIPTS:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, script, "--help"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_resolve_run_direct_script_returns_frontend(self):
        result = subprocess.run(
            [
                sys.executable,
                "automation/learning/resolve_run.py",
                "--event-name",
                "workflow_dispatch",
                "--manual-domain",
                "frontend",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "frontend")


if __name__ == "__main__":
    unittest.main()
