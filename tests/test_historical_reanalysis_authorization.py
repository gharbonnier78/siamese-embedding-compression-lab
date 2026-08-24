from __future__ import annotations

import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "protocol/authorizations/study_0_historical_reanalysis_v0.2.2.yaml"
COVERAGE_CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY1 = ROOT / "protocol/studies/study_1_face_backbone.yaml"
PREFLIGHT = runpy.run_path(str(ROOT / "scripts/preflight_study0_historical_reanalysis.py"))
VALIDATE = PREFLIGHT["validate_historical_reanalysis_authorization"]
ASSERT_MERGED = PREFLIGHT["assert_authorization_merged_to_main"]
NON_EXECUTING_STUDY1_STATUSES = PREFLIGHT["NON_EXECUTING_STUDY1_STATUSES"]


class HistoricalReanalysisAuthorizationTests(unittest.TestCase):
    def _assert_mutation_rejected(self, mutate, pattern: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.yaml"
            authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
            mutate(authorization)
            path.write_text(yaml.safe_dump(authorization, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, pattern):
                VALIDATE(path)

    def test_repository_authorization_contract_is_scoped(self) -> None:
        authorization = VALIDATE(AUTHORIZATION)
        self.assertEqual(
            authorization["scope"]["execution_step"],
            "corrected_study_0_reanalysis",
        )
        self.assertTrue(authorization["historical_study_0_scores_permitted"])
        self.assertTrue(authorization["researcher_go"]["explicit"])
        self.assertTrue(authorization["researcher_go"]["scope_change_requires_new_go"])

    def test_frozen_coverage_contract_remains_historical_read_false(self) -> None:
        contract = yaml.safe_load(COVERAGE_CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(contract["historical_study_0_scores_permitted"])

    def test_authorization_does_not_start_study_1(self) -> None:
        study1 = yaml.safe_load(STUDY1.read_text(encoding="utf-8"))
        authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
        self.assertIn(study1["status"], NON_EXECUTING_STUDY1_STATUSES)
        self.assertFalse(authorization["restrictions"]["study_1_execution_permitted"])
        self.assertFalse(authorization["restrictions"]["geometry_exploration_permitted"])

    def test_wrong_execution_scope_is_rejected(self) -> None:
        self._assert_mutation_rejected(
            lambda authorization: authorization["scope"].__setitem__(
                "execution_step", "study_1_execution"
            ),
            "corrected_study_0_reanalysis only",
        )

    def test_missing_researcher_go_is_rejected(self) -> None:
        self._assert_mutation_rejected(
            lambda authorization: authorization["researcher_go"].__setitem__("explicit", False),
            "explicit researcher GO",
        )

    def test_scope_change_without_new_go_rule_is_rejected(self) -> None:
        self._assert_mutation_rejected(
            lambda authorization: authorization["researcher_go"].__setitem__(
                "scope_change_requires_new_go", False
            ),
            "scope changes must require a new GO",
        )

    def test_method_broadening_is_rejected(self) -> None:
        self._assert_mutation_rejected(
            lambda authorization: authorization["restrictions"].__setitem__(
                "retraining_permitted", True
            ),
            "retraining_permitted=false",
        )

    def test_additional_contract_drift_cases_are_rejected(self) -> None:
        cases = [
            (
                "wrong prerequisite merge",
                lambda authorization: authorization["prerequisites"].__setitem__(
                    "prerequisite_merge_sha", "deadbeef"
                ),
                "anchored to the reviewed PR #31 merge",
            ),
            (
                "wrong historical run",
                lambda authorization: authorization["scope"].__setitem__(
                    "historical_run_id", "wrong-run"
                ),
                "authorization historical run differs",
            ),
            (
                "wrong study id",
                lambda authorization: authorization["scope"].__setitem__(
                    "study_id", "study_1_face_backbone"
                ),
                "Study 0 v0.2.2 only",
            ),
            (
                "wrong seeds",
                lambda authorization: authorization["execution_contract"].__setitem__(
                    "seeds", [11, 29]
                ),
                "authorization seeds differ",
            ),
            (
                "wrong bootstrap count",
                lambda authorization: authorization["execution_contract"].__setitem__(
                    "bootstrap_replicates", 9999
                ),
                "bootstrap count differs",
            ),
            (
                "wrong sampling unit",
                lambda authorization: authorization["execution_contract"].__setitem__(
                    "sampling_unit", "pair"
                ),
                "sampling unit differs",
            ),
            (
                "wrong degeneracy action",
                lambda authorization: authorization["execution_contract"].__setitem__(
                    "degenerate_replicate_action", "SKIP"
                ),
                "degeneracy action differs",
            ),
            (
                "score recomputation enabled",
                lambda authorization: authorization["restrictions"].__setitem__(
                    "score_recomputation_permitted", True
                ),
                "score_recomputation_permitted=false",
            ),
            (
                "all pairs enabled",
                lambda authorization: authorization["restrictions"].__setitem__(
                    "all_pairs_generation_permitted", True
                ),
                "all_pairs_generation_permitted=false",
            ),
            (
                "wrong coverage gate path",
                lambda authorization: authorization["prerequisites"]["coverage_gate"].__setitem__(
                    "path", "wrong.json"
                ),
                "coverage gate path",
            ),
            (
                "wrong required gate status",
                lambda authorization: authorization["prerequisites"]["coverage_gate"].__setitem__(
                    "required_status", "FAIL"
                ),
                "gate prerequisite is not satisfied",
            ),
            (
                "wrong selected checkpoint",
                lambda authorization: authorization["prerequisites"]["coverage_gate"].__setitem__(
                    "selected_dataset_checkpoint", 2000
                ),
                "checkpoint does not match",
            ),
            (
                "wrong review path",
                lambda authorization: authorization["prerequisites"][
                    "independent_coverage_review"
                ].__setitem__("path", "wrong.md"),
                "review path",
            ),
            (
                "wrong chronicle resolution",
                lambda authorization: authorization["prerequisites"].__setitem__(
                    "chronicle_resolution", "CHRON-wrong"
                ),
                "depend on CHRON-20260819-008",
            ),
        ]

        for name, mutate, pattern in cases:
            with self.subTest(name=name):
                self._assert_mutation_rejected(mutate, pattern)

    @mock.patch("subprocess.run")
    def test_merge_activation_rejects_unmerged_head(self, run: mock.Mock) -> None:
        def fake_run(args, **kwargs):
            del kwargs
            if args == ["git", "rev-parse", "HEAD"]:
                return subprocess.CompletedProcess(args, 0, stdout="pr-head\n")
            if args[:4] == ["git", "show-ref", "--verify", "--quiet"]:
                return subprocess.CompletedProcess(args, 0)
            if args[:3] == ["git", "merge-base", "--is-ancestor"]:
                return subprocess.CompletedProcess(args, 1)
            raise AssertionError(f"unexpected git invocation: {args}")

        run.side_effect = fake_run
        with self.assertRaisesRegex(RuntimeError, "not reachable from main"):
            ASSERT_MERGED()

    @mock.patch("subprocess.run")
    def test_merge_activation_fails_closed_without_main_ref(self, run: mock.Mock) -> None:
        def fake_run(args, **kwargs):
            del kwargs
            if args == ["git", "rev-parse", "HEAD"]:
                return subprocess.CompletedProcess(args, 0, stdout="head\n")
            if args[:4] == ["git", "show-ref", "--verify", "--quiet"]:
                return subprocess.CompletedProcess(args, 1)
            raise AssertionError(f"unexpected git invocation: {args}")

        run.side_effect = fake_run
        with self.assertRaisesRegex(RuntimeError, "no local origin/main or main ref"):
            ASSERT_MERGED()

    @mock.patch("subprocess.run")
    def test_merge_activation_accepts_head_reachable_from_main(self, run: mock.Mock) -> None:
        def fake_run(args, **kwargs):
            del kwargs
            if args == ["git", "rev-parse", "HEAD"]:
                return subprocess.CompletedProcess(args, 0, stdout="merged-head\n")
            if args == [
                "git",
                "show-ref",
                "--verify",
                "--quiet",
                "refs/remotes/origin/main",
            ]:
                return subprocess.CompletedProcess(args, 0)
            if args == [
                "git",
                "merge-base",
                "--is-ancestor",
                "merged-head",
                "refs/remotes/origin/main",
            ]:
                return subprocess.CompletedProcess(args, 0)
            raise AssertionError(f"unexpected git invocation: {args}")

        run.side_effect = fake_run
        self.assertEqual(ASSERT_MERGED(), "refs/remotes/origin/main")


if __name__ == "__main__":
    unittest.main()
