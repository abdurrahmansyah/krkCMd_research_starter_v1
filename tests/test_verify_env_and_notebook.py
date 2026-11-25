"""
tests/test_verify_env_and_notebook.py

Unit tests for portable Jupyter kernel discovery and verification logic (M01.1 Section L).
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_env_and_notebook import inspect_kernelspecs  # noqa: E402


class TestPortableKernelVerification(unittest.TestCase):
    def test_auto_discovers_matching_project_kernel(self) -> None:
        exp_py = Path(sys.executable).resolve()
        specs = {
            "python3": {"spec": {"display_name": "Python 3", "argv": ["C:/nonexistent/python.exe", "-m", "ipykernel_launcher"]}},
            "krkcmd-research-newpc": {"spec": {"display_name": "Python (krkCMd Research - New PC)", "argv": [str(exp_py), "-m", "ipykernel_launcher"]}},
        }
        res = inspect_kernelspecs(specs, requested_kernel=None, expected_python=exp_py)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["selected_kernel"], "krkcmd-research-newpc")
        self.assertEqual(res["failures"], [])

    def test_missing_requested_kernel_gives_friendly_error(self) -> None:
        exp_py = Path(sys.executable).resolve()
        specs = {
            "krkcmd-research-newpc": {"spec": {"display_name": "New PC", "argv": [str(exp_py)]}},
        }
        res = inspect_kernelspecs(specs, requested_kernel="krkcmd-research", expected_python=exp_py)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("not registered", res["failures"][0])
        self.assertIn("krkcmd-research-newpc", res["failures"][0])

    def test_stale_interpreter_path_detected(self) -> None:
        exp_py = Path(sys.executable).resolve()
        specs = {
            "krkcmd-research": {"spec": {"display_name": "Old PC", "argv": ["C:/Users/OldUser/missing/python.exe"]}},
        }
        res = inspect_kernelspecs(specs, requested_kernel="krkcmd-research", expected_python=exp_py)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("missing/stale interpreter", res["failures"][0])

    def test_mismatched_existing_interpreter_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            other_py = Path(tmpdir) / "other_python.exe"
            other_py.write_text("stub", encoding="utf-8")
            exp_py = Path(sys.executable).resolve()
            specs = {
                "krkcmd-other": {"spec": {"display_name": "Other", "argv": [str(other_py)]}},
            }
            res = inspect_kernelspecs(specs, requested_kernel="krkcmd-other", expected_python=exp_py)
            self.assertEqual(res["status"], "FAIL")
            self.assertIn("does not match expected Python", res["failures"][0])


if __name__ == "__main__":
    unittest.main()
