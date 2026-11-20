"""Shared access to solver-independent deterministic results."""

import json

import pytest


@pytest.fixture
def solution_record(tmp_path):
    """Read the latest result through Gana's public solution export."""

    def read(program):
        path = tmp_path / "solution.json"
        program.export_solution(path)
        return json.loads(path.read_text())

    return read
