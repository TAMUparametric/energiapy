class Element(Dunders, Magics):
    """The usual dunders for Model Elements"""

    @classmethod
    def _elm(cls) -> str:
        """Returns element class name"""
        return cls.__name__

    @staticmethod
    def _iselm():
        return True
