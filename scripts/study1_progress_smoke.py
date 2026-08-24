from __future__ import annotations

import argparse
from pathlib import Path

from siamese_compression_lab.study1_progress import (
    ParentProgressReporter,
    ProgressConfig,
    resume_count_for_block,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/study1-progress-smoke"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    config = ProgressConfig(
        stage="embedding_512d_smoke",
        unit="images",
        block_id="smoke-images-0000000-0000100",
        block_start=0,
        block_stop=100,
        report_every=25,
        workers=args.workers,
        campaign_total=100,
        campaign_completed_before_block=0,
    )
    resumed = resume_count_for_block(progress_path, config)
    reporter = ParentProgressReporter(progress_path, config, resumed_completed=resumed)
    for completed in range(resumed + 1, 101):
        reporter.update(completed)
    reporter.complete()
    print(progress_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
