"""Compatibility shim for directly executed learning package scripts.

GitHub Actions invokes helpers as file paths (for example,
``python automation/learning/resolve_run.py``). In that mode Python places
``automation/learning`` on ``sys.path`` instead of the repository root, so
absolute imports such as ``automation.learning.contracts`` cannot resolve the
repository's namespace package.

When this file is discovered as the top-level ``automation`` module during a
direct script invocation, exposing ``automation/`` as ``__path__`` makes the
module package-like and restores the same import layout used by normal package
imports. Normal imports from the repository root continue to use the namespace
package directory and do not load this shim.
"""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[1])]
