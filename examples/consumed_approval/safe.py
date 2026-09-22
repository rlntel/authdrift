"""Corrected variant: re-evaluate current authority after the checkpoint."""

from pathlib import Path
import runpy

_factory = runpy.run_path(str(Path(__file__).with_name("scenario.py")))["build_scenario"]


def build_scenario():
    return _factory(safe=True)
