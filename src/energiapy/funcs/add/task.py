from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...types.alias import IsTask, IsValue


def add_task(task: IsTask, value: IsValue):
    """Adds a value to a Task"""
