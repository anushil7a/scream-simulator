"""Entry point for the current bounded recovery policy regressions.
Historical characterization results remain in tests/evidence and Git history.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('profile_recovery_policy.py')),run_name='__main__')
