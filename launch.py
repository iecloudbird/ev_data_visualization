#!/usr/bin/env python3
"""
Cross-platform launcher for EV Data Visualization.
- Creates/activates virtual environment
- Installs dependencies (relaxed by default, or locked with --locked)
- Optionally runs the notebook pipeline
- Launches the Dash dashboard

Usage:
  python launch.py                 # install (if needed) and launch dashboard
  python launch.py --pipeline      # run pipeline, then launch dashboard
  python launch.py --skip-map      # skip map notebook when running pipeline
  python launch.py --locked        # install using constraints for exact versions
  python launch.py --no-dashboard  # install only (and pipeline if requested)
"""
from __future__ import annotations
import os
import sys
import subprocess
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
VENV_PY = VENV_DIR / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")


def ensure_venv() -> None:
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        rc = subprocess.call([sys.executable, "-m", "venv", str(VENV_DIR)])
        if rc != 0:
            raise SystemExit("Failed to create virtual environment")
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")


def install_deps(locked: bool) -> None:
    # Upgrade pip for better resolver
    subprocess.check_call([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip"]) 

    cmd = [str(VENV_PY), "-m", "pip", "install", "-r", "requirements.txt"]
    if locked and (ROOT / "requirements-constraints.txt").exists():
        cmd += ["-c", "requirements-constraints.txt"]
        print("Installing with constraints (locked versions)...")
    else:
        print("Installing with relaxed requirements...")

    rc = subprocess.call(cmd, cwd=str(ROOT))
    if rc != 0:
        raise SystemExit("Dependency installation failed")


def run_pipeline(skip_map: bool) -> None:
    runner = ROOT / "scripts" / "run_pipeline.py"
    if not runner.exists():
        print("Pipeline runner not found; skipping.")
        return
    cmd = [str(VENV_PY), str(runner)]
    if skip_map:
        cmd.append("--skip-map")
    rc = subprocess.call(cmd, cwd=str(ROOT))
    if rc != 0:
        raise SystemExit("Notebook pipeline failed")


def run_metrics_script() -> None:
    """Run the one-time metrics calculation script to populate data/processed/metrics/."""
    metrics_script = ROOT / "notebooks" / "data_wrangling" / "calculate_metrics.py"
    if not metrics_script.exists():
        print("Metrics script not found; skipping calculate_metrics.py.")
        return
    print("Running metrics script (calculate_metrics.py)...")
    rc = subprocess.call([str(VENV_PY), str(metrics_script)], cwd=str(ROOT))
    if rc != 0:
        raise SystemExit("Metrics script calculate_metrics.py failed")


def launch_dashboard() -> None:
    print("Launching dashboard at http://localhost:8050")
    rc = subprocess.call([str(VENV_PY), "-m", "dashboard.app"], cwd=str(ROOT))
    if rc != 0:
        raise SystemExit("Dashboard exited with error")


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Cross-platform project launcher")
    p.add_argument("--pipeline", action="store_true", help="Run notebook pipeline before launching dashboard")
    p.add_argument("--skip-map", action="store_true", help="Skip the map notebook when running pipeline")
    p.add_argument("--locked", action="store_true", help="Install using requirements-constraints.txt for exact versions")
    p.add_argument("--no-dashboard", action="store_true", help="Do not launch the dashboard")
    args = p.parse_args()

    ensure_venv()
    install_deps(locked=args.locked or os.environ.get("EV_LOCKED") == "1")

    if args.pipeline:
        run_pipeline(skip_map=args.skip_map)
        run_metrics_script()

    if not args.no_dashboard:
        launch_dashboard()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
