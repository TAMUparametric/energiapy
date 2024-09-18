"""Classifies the input as upper or lower bound or fixed (incidental)
"""

from dataclasses import dataclass, field


@dataclass
class _Bnds:
    """Lower and Upper Bounds"""

    lb: int | float | list
    ub: int | float | list

    def __post_init__(self):

        if isinstance(self.lb, (int, float)):
            self.lb = [self.lb]

        if isinstance(self.ub, (int, float)):
            self.ub = [self.ub]

        if len(self.lb) != len(self.ub):
            if len(self.lb) == 1:
                self.lb = self.lb * len(self.ub)

            elif len(self.ub) == 1:
                self.ub = self.ub * len(self.lb)

            else:
                raise ValueError(
                    'Lower and Upper bounds must be of same length, or one of them must be a scalar'
                )


@dataclass
class In(_Bnds):
    """Used when declaring that the parameter lies in the given domain

    When In is used, the parameter is treated as multiparemetric variable

    Attributes:
        lb (int | float | list): lower bound
        ub (int | float | list): upper bound

    """

    def __post_init__(self):
        _Bnds.__post_init__(self)

        self.space = (self.lb, self.ub)


@dataclass
class Btwn(_Bnds):
    """Used when there is an lower bound or upper bound on the input
    The value can be anything between the lower and upper bound

    Attributes:
        lb (int | float | list | In): lower bound
        ub (bool | int | float | list | In): upper bound
        lb_penalty (int | float | list): penalty for lower bound
        ub_penalty (int | float | list): penalty for upper bound
    """

    lb_penalty: int | float | list = field(default=None)
    ub_penalty: int | float | list = field(default=None)

    def __post_init__(self):
        if self.lb and not self.ub:
            self.ub = True

        if self.ub and not self.lb:
            self.lb = 0

        _Bnds.__post_init__(self)


@dataclass
class And:
    """Used when there is an incidental value along with the input
    The incidental value will be incurred irrespective of the parent decision variable

    Attributes:
        value (int | float | list | tuple[int | float | list]): value scales with parent variable
        incidental (int | float | list | tuple[int | float | list]): incidental value is fixed

    """

    value: int | float | list | In = field(default=None)
    incidental: int | float | list | In = field(default=None)
