import re
import unittest
from pathlib import Path


WORKFLOW = Path('.github/workflows/muse-learning.yml')


def workflow_text():
    return WORKFLOW.read_text(encoding='utf-8')


def job_section(text: str, job: str) -> str:
    match = re.search(rf'^  {re.escape(job)}:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_]+:\n|\Z)', text, re.M | re.S)
    if not match:
        raise AssertionError(f'missing job {job}')
    return match.group(0)


class WorkflowContractTest(unittest.TestCase):
    def test_schedule_and_manual_dry_run_contract(self):
        text = workflow_text()
        for cron in ('0 3 * * 1', '0 3 * * 3', '0 3 * * 5'):
            self.assertIn(f"cron: '{cron}'", text)
        self.assertEqual(text.count("timezone: 'Asia/Shanghai'"), 3)
        self.assertIn('workflow_dispatch:', text)
        dry_run_block = re.search(r'dry_run:\n(?P<body>(?:\s{8,}.*\n)+)', text)
        self.assertIsNotNone(dry_run_block)
        self.assertIn('default: true', dry_run_block.group('body'))
        self.assertIn("vars.MUSE_LEARNING_SCHEDULE_ENABLED == 'true'", text)

    def test_actions_are_sha_pinned_and_checkout_does_not_persist_credentials(self):
        text = workflow_text()
        refs = re.findall(r'^\s*-?\s*uses:\s*(actions/[^@\s]+)@([^\s]+)', text, re.M)
        self.assertGreaterEqual(len(refs), 10)
        for action, ref in refs:
            self.assertRegex(ref, r'^[0-9a-f]{40}$', action)
        checkout_count = len(re.findall(r'uses:\s*actions/checkout@', text))
        self.assertGreaterEqual(checkout_count, 5)
        self.assertEqual(text.count('persist-credentials: false'), checkout_count)

    def test_every_muse_run_is_sandboxed_bounded_and_secret_scanned(self):
        text = workflow_text()
        muse_count = text.count('muse exec ')
        self.assertEqual(muse_count, 3)
        self.assertEqual(text.count('--sandbox-network restricted'), muse_count)
        self.assertEqual(text.count('--max-model-steps'), muse_count)
        self.assertGreaterEqual(text.count('secret_guard.py'), muse_count)
        self.assertNotIn('--yolo', text)
        self.assertNotIn('--disable-sandbox', text)
        self.assertNotIn('--sandbox-network unrestricted', text)

    def test_muse_jobs_are_read_only_and_publish_jobs_never_run_muse(self):
        text = workflow_text()
        for job in ('plan', 'synthesize', 'draft_skill_candidate'):
            section = job_section(text, job)
            self.assertIn('contents: read', section)
            self.assertNotIn('contents: write', section)
            self.assertNotIn('pull-requests: write', section)
        for job in ('publish_learning', 'publish_skill_candidate'):
            section = job_section(text, job)
            self.assertIn('contents: write', section)
            self.assertIn('pull-requests: write', section)
            self.assertNotIn('muse exec', section)
            self.assertNotIn('META_API_KEY', section)
            self.assertIn('gh pr create', section)

    def test_untrusted_processing_has_immutable_workspace_guards_before_repo_validators(self):
        text = workflow_text()
        plan = job_section(text, 'plan')
        synth = job_section(text, 'synthesize')
        draft = job_section(text, 'draft_skill_candidate')
        self.assertLess(plan.index('Planning changed tracked repository files.'), plan.index('secret_guard.py'))
        self.assertLess(synth.index('Synthesis changed unauthorized repository paths'), synth.index('secret_guard.py'))
        self.assertIn('pre-skill-learning.patch', draft)
        self.assertIn('post-skill-learning.patch', draft)
        self.assertIn('cmp -s', draft)
        self.assertLess(draft.index('cmp -s'), draft.index('secret_guard.py'))

    def test_publish_paths_are_revalidated_before_push(self):
        text = workflow_text()
        learning = job_section(text, 'publish_learning')
        skill = job_section(text, 'publish_skill_candidate')
        self.assertIn('validate_learning_output.py', learning)
        self.assertLess(learning.index('validate_learning_output.py'), learning.index('git push'))
        self.assertIn('validate_skill_candidate.py', skill)
        self.assertLess(skill.index('validate_skill_candidate.py'), skill.index('git push'))
        self.assertIn('test "$CHANGED" = "$TARGET"', skill)


if __name__ == '__main__':
    unittest.main()
