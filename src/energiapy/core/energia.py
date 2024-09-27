"""An energiapy object"""


class Energia:
    """An energiapy object
    Inherited by all classes in the package
    """

    def __init__(self, name: str = None):
        self.name = name

    def __repr__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)
