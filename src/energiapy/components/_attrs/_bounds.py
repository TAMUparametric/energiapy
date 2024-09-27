"""Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field, fields

# from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _Transact:
    """Exchange of Cash"""





class _BoundAttrs:
    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return [
            f.name
            for f in fields(_Transact)
            + fields(_Emit)
            + fields(_Trade)
            + fields(_Use)
            + fields(_Setup)
        ]
