#!/usr/bin/env python3
"""
Run project notebooks in order for reproducibility.

- Tries papermill first (parameterizable, rich output)
- Falls back to jupyter nbconvert --execute if papermill not installed
- Provides options to skip heavy notebooks

Usage:
  python scripts/run_pipeline.py              # run all
  python scripts/run_pipeline.py --skip-map   # skip map notebook
  python scripts/run_pipeline.py --list       # list notebooks

Exit codes:
  0 = success, 1 = failure in any notebook
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"

PIPELINE = [
    NB / "data_cleaning" / "dp_fill_2024.ipynb",
    NB / "data_wrangling" / "merge_ev_stations.ipynb",
    NB / "data_wrangling" / "transform_data.ipynb",
    NB / "merge_datasets.ipynb",
    NB / "ev.ipynb",
    NB / "data_visualization" / "ev_stations_map.ipynb",
]

HEAVY = {
    str(NB / "data_visualization" / "ev_stations_map.ipynb"),
}

def has_papermill() -> bool:
    try:
        import papermill  # noqa: F401
        return True
    except Exception:
        return False


def run_with_papermill(nb_path: Path) -> int:
    cmd = [
        sys.executable, "-m", "papermill",
        str(nb_path), str(nb_path)  # in-place execution
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


def run_with_nbconvert(nb_path: Path) -> int:
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "notebook",
        "--inplace",
        "--execute",
        "--ExecutePreprocessor.timeout=1200",
        str(nb_path),
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Execute project notebooks in order")
    parser.add_argument("--skip-map", action="store_true", help="Skip the interactive map notebook")
    parser.add_argument("--list", action="store_true", help="List notebooks without executing")
    args = parser.parse_args()

    notebooks = [str(p) for p in PIPELINE]
    if args.skip_map:
        notebooks = [p for p in notebooks if p not in HEAVY]

    if args.list:
        print("\nExecution order:")
        for i, p in enumerate(notebooks, 1):
            print(f" {i}. {Path(p).relative_to(ROOT)}")
        return 0

    use_papermill = has_papermill()
    if use_papermill:
        print("Using papermill for execution")
    else:
        print("papermill not found; falling back to jupyter nbconvert --execute")

    failures = []
    for idx, nb in enumerate(notebooks, 1):
        rel = str(Path(nb).relative_to(ROOT))
        print("=" * 80)
        print(f"[{idx}/{len(notebooks)}] Executing {rel}")
        print("=" * 80)
        rc = run_with_papermill(Path(nb)) if use_papermill else run_with_nbconvert(Path(nb))
        if rc != 0:
            print(f"ERROR: Execution failed for {rel} (exit code {rc})")
            failures.append(rel)
            break
        else:
            print(f"OK: {rel}")

    if failures:
        print("\nFailures:")
        for f in failures:
            print(f" - {f}")
        return 1

    print("\nAll notebooks executed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
