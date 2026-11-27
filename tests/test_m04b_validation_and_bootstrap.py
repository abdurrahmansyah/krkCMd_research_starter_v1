import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from evaluation.m04b_bootstrap import run_paired_cluster_bootstrap  # noqa: E402
from consolidate_m04b import validate_attempt_dir  # noqa: E402


class TestM04BValidationAndBootstrap(unittest.TestCase):
    def test_bootstrap_reproducibility_alignment_and_multiplicity(self):
        rng = np.random.default_rng(123)
        # Unequal cluster sizes: 10, 20, 30, 40
        clusters = np.array(["C1"] * 10 + ["C2"] * 20 + ["C3"] * 30 + ["C4"] * 40)
        y_true = rng.uniform(0.0, 200.0, size=len(clusters))
        preds = {
            "M1": y_true + rng.normal(0.0, 5.0, size=len(clusters)),
            "ML01": y_true + rng.normal(0.0, 10.0, size=len(clusters)),
            "CONST": np.full(len(clusters), 50.0),
        }

        m1, p1, draws1, _ = run_paired_cluster_bootstrap(preds, y_true, clusters, comparators=("ML01",), n_boot=200, seed=42)
        m2, p2, draws2, _ = run_paired_cluster_bootstrap(preds, y_true, clusters, comparators=("ML01",), n_boot=200, seed=42)

        np.testing.assert_array_equal(draws1, draws2)
        pd.testing.assert_frame_equal(m1, m2)
        pd.testing.assert_frame_equal(p1, p2)

        # CI ordering
        for _, row in m1.iterrows():
            self.assertLessEqual(row["mae_ci_low_um"], row["mae_ci_high_um"])
            self.assertLessEqual(row["rmse_ci_low_um"], row["rmse_ci_high_um"])

        # Constant prediction -> CCC undefined (None/NaN, 0 valid replicates), never 0.0
        const_row = m1.loc[m1["model_id"] == "CONST"].iloc[0]
        self.assertTrue(pd.isna(const_row["ccc_point"]))
        self.assertEqual(int(const_row["ccc_valid_replicates"]), 0)

        # Paired difference sign & CI ordering
        diff_row = p1.loc[p1["candidate_id"] == "M1"].iloc[0]
        self.assertLess(diff_row["delta_mae_point_um"], 0.0)
        self.assertLessEqual(diff_row["delta_mae_ci_low_um"], diff_row["delta_mae_ci_high_um"])

    def test_pooled_mae_denominator_unequal_clusters(self):
        # Cluster A has 1 row with err=100; Cluster B has 99 rows with err=0.
        # True pooled MAE = 100 / 100 = 1.0 (NOT equal-cluster mean 50.0).
        clusters = np.array(["A"] * 1 + ["B"] * 99)
        y_true = np.zeros(100)
        y_pred = np.array([100.0] + [0.0] * 99)
        m, _, _, _ = run_paired_cluster_bootstrap({"M": y_pred}, y_true, clusters, comparators=(), n_boot=50, seed=42)
        self.assertAlmostEqual(float(m.iloc[0]["mae_point_um"]), 1.0)

    def test_strengthened_attempt_validator_rejects_invalid_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            att = Path(tmp) / "M04A_ML01_scientific_v1_s42"
            att.mkdir(parents=True)
            val_ids = [0, 1, 2]
            y_exp = np.array([10.0, 20.0, 30.0])

            def write_valid():
                (att / "runner_result.json").write_text(
                    json.dumps({"returncode": 0, "timed_out": False, "violation_reason": None, "suspend_detected": False}),
                    encoding="utf-8",
                )
                (att / "worker_result.json").write_text(
                    json.dumps({
                        "status": "PASS",
                        "model_id": "ML01",
                        "attempt_id": f"attempts/{att.name}",
                        "config_id": "scientific_v1",
                        "data_audit": {"test_rows_exposed_to_worker": 0},
                    }),
                    encoding="utf-8",
                )
                pd.DataFrame({
                    "source_row_id": val_ids,
                    "y_true_um": y_exp,
                    "y_pred_raw_um": y_exp,
                    "y_pred_nonnegative_um": y_exp,
                }).to_csv(att / "predictions.csv", index=False)

            write_valid()
            ok, reason, *_ = validate_attempt_dir(att, "ML01", val_ids, y_exp)
            self.assertTrue(ok, reason)

            # Nonzero exit
            (att / "runner_result.json").write_text(json.dumps({"returncode": 1, "timed_out": False, "violation_reason": None, "suspend_detected": False}), encoding="utf-8")
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Timeout
            (att / "runner_result.json").write_text(json.dumps({"returncode": 0, "timed_out": True, "violation_reason": None, "suspend_detected": False}), encoding="utf-8")
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Resource violation
            (att / "runner_result.json").write_text(json.dumps({"returncode": 0, "timed_out": False, "violation_reason": "VRAM", "suspend_detected": False}), encoding="utf-8")
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Suspend detected
            (att / "runner_result.json").write_text(json.dumps({"returncode": 0, "timed_out": False, "violation_reason": None, "suspend_detected": True}), encoding="utf-8")
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Wrong config_id
            write_valid()
            wr = json.loads((att / "worker_result.json").read_text(encoding="utf-8"))
            wr["config_id"] = "compat_v1"
            (att / "worker_result.json").write_text(json.dumps(wr), encoding="utf-8")
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Duplicate row IDs / wrong membership
            write_valid()
            pd.DataFrame({
                "source_row_id": [0, 0, 2],
                "y_true_um": y_exp,
                "y_pred_raw_um": y_exp,
                "y_pred_nonnegative_um": y_exp,
            }).to_csv(att / "predictions.csv", index=False)
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])

            # Missing predictions.csv
            (att / "predictions.csv").unlink()
            self.assertFalse(validate_attempt_dir(att, "ML01", val_ids, y_exp)[0])


if __name__ == "__main__":
    unittest.main()
