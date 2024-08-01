"""General classes for Components and Model Elements
"""


class Dunders:
    """The usual dunder methods for a Component
    """

    def __repr__(self):
        return str(getattr(self, 'name'))

    def __eq__(self, other):
        return getattr(self, 'name') == other.name

    def __hash__(self):
        return hash(getattr(self, 'name'))

    @classmethod
    def __init_subclass__(cls):
        cls.__hash__ = Dunders.__hash__
        cls.__eq__ = Dunders.__eq__
        cls.__repr__ = Dunders.__repr__


class Magics:
    """Magic functions
    """

    def __lt__(self, other):
        return getattr(self, 'name') < other.name

    def __gt__(self, other):
        return getattr(self, 'name') > other.name


class CmpCommon(Dunders, Magics):
    """The usual dunder methods for a Scenario Components
    """

    @classmethod
    def _cmp(cls) -> str:
        """Returns component class name
        """
        return cls.__name__

    @staticmethod
    def _iscomp():
        return True


class ElmCommon(Dunders, Magics):
    """The usual dunders for Model Elements
    """

    @classmethod
    def _elm(cls) -> str:
        """Returns element class name
        """
        return cls.__name__

    @staticmethod
    def _iselm():
        return True


class InpCommon(Dunders):
    """The usual dunders for Inputs
    """

    @classmethod
    def _inp(cls) -> str:
        """Returns input class name
        """
        return cls.__name__

    @staticmethod
    def _isinp():
        return True


class TskCommon(Dunders):
    """The usual dunders for Tasks
    """

    @classmethod
    def _tsk(cls) -> str:
        """Returns task class name
        """
        return cls.__name__

    @staticmethod
    def _istsk():
        return True


class ElmCollect:
    """Collect Model Elements associated with Object 
    """

    def __post_init__(self):
        for i in ['parameters', 'variables', 'constraints', 'ctypes']:
            setattr(self, i, [])

    def params(self):
        """prints parameters of the Object
        """
        for i in getattr(self, 'parameters'):
            print(i)

    def vars(self):
        """prints variables of the Object
        """
        for i in getattr(self, 'variables'):
            print(i)

    def cons(self):
        """prints constraints of the Object
        """
        for i in getattr(self, 'constraints'):
            print(i)
