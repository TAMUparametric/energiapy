"""Default Temporal Horizon 
"""

from dataclasses import dataclass, field
import calendar

@dataclass
class _Calendar:
    rng_year: tuple[int, int] = field(default=None)
    rng_month: tuple[tuple[int, int], tuple[int, int]] = field(default=None)
    rng_week: tuple[tuple[int, int], tuple[int, int]] = field(default=None)
    rng_day: tuple[tuple[int, int], tuple[int, int]] = field(default=None)
    rng_hour: tuple[tuple[int, int], tuple[int, int]] = field(default=None)
    rng_minute: tuple[tuple[int, int], tuple[int, int]] = field(default=None)
    def_year: bool = field(default=False)
    def_month: bool = field(default=False)
    def_week: bool = field(default=False)
    def_day: bool = field(default=False)
    def_hour: bool = field(default=False)
    def_minute: bool = field(default=False)

    
