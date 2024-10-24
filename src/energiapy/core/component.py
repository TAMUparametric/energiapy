"""An energiapy object"""

from .....gana.src.gana.block.prg import Prg



class Component:
    """This is inherited by all Components

    Personalizes the Component based on the attribute name set in Scenario

    Also adds Model and reports individual Blocks of the Model

    Attributes:
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    def __init__(
        self,
        name: str = None,
        basis: str = None,
        cite: dict = None,
        introduce: str = None,
        retire: str = None,
        label: str = None,
    ):
        self.name = name
        self.basis = basis
        self.cite = cite
        self.introduce = introduce
        self.retire = retire
        self.label = label
        # this is the name of the component

        # Will be generated by TaskMaster based on user input
        self.program: Prg = None

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
