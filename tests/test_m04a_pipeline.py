import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluation.experiment_runner import ExperimentSpec, execute_experiment  # noqa: E402
from evaluation.m04a_data import FEATURE_COLS, TARGET_COL, load_protocol_a_train_val  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    compute_engineering_tolerances,
    compute_measurement_agreement,
    compute_predictive_accuracy,
    compute_robustness_summary,
)


class TestM04APipelineAndGuards(unittest.TestCase):
    def test_raw_schema_and_strict_test_exclusion(self):
        raw_csv = ROOT / "data" / "raw" / "krkCMd_table.csv"
        manifest = ROOT / "reports" / "tables" / "group_split_manifest.csv"
        data = load_protocol_a_train_val(raw_csv, manifest, authorized_phase="M04A_PROTOCOL_A_TRAIN_VAL", seed=42)

        self.assertEqual(data.X_train.shape, (12216, 501))
        self.assertEqual(data.X_val.shape, (3060, 501))
        self.assertEqual(len(FEATURE_COLS), 501)
        self.assertEqual(TARGET_COL, "MANwidth")
        self.assertEqual(data.audit["test_rows_excluded"], 3822)
        self.assertEqual(data.audit["test_rows_exposed_to_worker"], 0)
        self.assertTrue((data.train_meta["split"] == "train").all())
        self.assertTrue((data.val_meta["split"] == "validation").all())

        # Group-aware inner validation has zero group_id overlap
        in_tr_groups = set(data.train_meta.loc[data.train_inner_mask, "group_id"])
        in_val_groups = set(data.train_meta.loc[~data.train_inner_mask, "group_id"])
        self.assertEqual(len(in_tr_groups & in_val_groups), 0)

    def test_unauthorized_phase_rejected(self):
        raw_csv = ROOT / "data" / "raw" / "krkCMd_table.csv"
        manifest = ROOT / "reports" / "tables" / "group_split_manifest.csv"
        with self.assertRaises(PermissionError):
            load_protocol_a_train_val(raw_csv, manifest, authorized_phase="PROTOCOL_A_TEST")

    def test_attempt_directory_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            attempt_dir = out_dir / "RUN_X" / "ATTEMPT_1"
            attempt_dir.mkdir(parents=True)
            (attempt_dir / "worker_result.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")

            spec = ExperimentSpec(
                model_id="RF01",
                config_id="scientific_v1",
                run_id="RUN_X",
                attempt_id="ATTEMPT_1",
                split_manifest="dummy.csv",
                seed=42,
                environment_executable=sys.executable,
                worker_module="src.evaluation.m04a_scientific_worker",
                authorize_real_data_training=True,
            )
            with self.assertRaises(FileExistsError):
                execute_experiment(spec, out_dir)

    def test_raw_vs_clipped_and_empty_robustness_handling(self):
        y_true = np.array([0.0, 10.0, 20.0, 50.0])
        y_raw = np.array([-5.0, 12.0, 18.0, 48.0])
        y_clip = np.maximum(0.0, y_raw)

        m_raw = compute_predictive_accuracy(y_true, y_raw)
        m_clip = compute_predictive_accuracy(y_true, y_clip)
        self.assertGreater(m_raw["mae_um"], m_clip["mae_um"])
        self.assertAlmostEqual(m_raw["mae_um"], (5.0 + 2.0 + 2.0 + 2.0) / 4.0)
        self.assertAlmostEqual(m_clip["mae_um"], (0.0 + 2.0 + 2.0 + 2.0) / 4.0)

        ag = compute_measurement_agreement(y_true, y_raw)
        self.assertIsNotNone(ag["lins_ccc"])
        tol = compute_engineering_tolerances(y_true, y_raw)
        self.assertIn("within_5um_rate", tol)

        rob_empty = compute_robustness_summary(y_true, y_raw, {})
        self.assertEqual(rob_empty["n_conditions"], 0)
        self.assertIsNone(rob_empty["mean_corrupted_mae_um"])


if __name__ == "__main__":
    unittest.main()
