"""Default Temporal Horizon"""

# from dataclasses import dataclass, field
# import calendar
# from typing import TypeAlias

# Rng: TypeAlias = tuple[tuple[int, int], tuple[int, int]] | tuple[tuple[int, int]]

# @dataclass
# class _Calendar:
#     rng_year: tuple[int, int] = field(default=None)
#     rng_month: Rng = field(
#         default=None
#     )
#     rng_week: Rng = field(
#         default=None
#     )
#     rng_day: Rng= field(
#         default=None
#     )
#     rng_hour: Rng = field(
#         default=None
#     )
#     rng_minute: Rng = field(
#         default=None
#     )
#     def_year: bool = field(default=False)
#     def_month: bool = field(default=False)
#     def_week: bool = field(default=False)
#     def_day: bool = field(default=False)
#     def_hour: bool = field(default=False)
#     def_minute: bool = field(default=False)

#     def __post_init__(self):
#         self._calendar = calendar.Calendar()
#         rng_attrs = [
#             'rng_year',
#             'rng_month',
#             'rng_week',
#             'rng_day',
#             'rng_hour',
#             'rng_minute',
#         ]

#         if sum(rng is not None for getattr(self, rng) in rng_attrs) > 1:
#             raise ValueError('Only one range attribute can be set')

#         rng = [getattr(self, rng) for rng in rng_attrs if getattr(self, rng) is not None]

#         for r in rng:
#             if self.range_year:
#                 year = r
#             else:
#                 year = r[0]

#             cal = self._calendar.yeardayscalendar(year, width=12)
#             if self.range_month:
#                 months = cal[r[1]]

#             if self.range_week:
