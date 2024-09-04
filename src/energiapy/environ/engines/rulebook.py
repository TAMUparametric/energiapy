"""Bhaskara for Constraint generation
"""

from dataclasses import dataclass, field
from operator import is_

from ...core._handy._dunders import _Dunders
from ...core.isalias.elms.isvar import IsVar
from ...core.nirop.errors import CacodcarError
from ..rule import Rule


@dataclass
class Bhaskara(_Dunders):
    """Bhaskara is rulebook for constraint generation

    Attributes:
        name (str): name of the Bhaskara, borrows from Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.rules = []
        self.name = f'RuleBook|{self.name}|'

    def make(self, rule: Rule):
        """Make and add Rule to RuleBook"""
        self.rules.append(rule)

    def find(self, variable: IsVar):
        """Fetch the rules that apply for a particular variable"""
        rule = [rule for rule in self.rules if is_(rule.variable, variable)]
        if rule:
            return rule
        else:
            raise CacodcarError(f'No Rule found for {variable.id()}')

    def vars(self):
        """Fetch all the Variables in the RuleBook"""
        return sorted([rule.variable for rule in self.rules], key=lambda x: x.cname())

    def prn_vars(self):
        """Fetch all the parent Variables in the RuleBook"""
        return sorted(
            [rule.variable.parent() for rule in self.rules if rule.variable.parent()],
            key=lambda x: x.cname(),
        )

    def prms(self):
        """Fetch all the Parameters in the RuleBook"""
        return sorted(
            [rule.parameter for rule in self.rules if rule.parameter],
            key=lambda x: x.cname(),
        )
