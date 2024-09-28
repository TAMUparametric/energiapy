"""3D Space
"""


class Dimension:
    """Space - represented by three dimensions
    
    dimension are representation through discretizations
    three discritizations are collected as elements of lists
    """

    def __init__(self, *dimensions):
        self.name = 'space'



    def __post_init__(self):
        self.name = f'Network|{self.name}|'
        self.locations: list[Location] = []
        self.linkages: list[Linkage] = []

    def __setattr__(self, name, component):

        if isinstance(component, Location):
            self.locations.append(component)

        if isinstance(component, Linkage):
            self.linkages.append(component)

        super().__setattr__(name, component)

    @property
    def nodes(self):
        """Nodes of the System are just Locations"""
        return self.locations

    @property
    def edges(self):
        """Edges of the System are just Linkages"""
        return self.linkages

    @property
    def pairs(self):
        """Source Sink pairs of the System"""
        return [(i.source, i.sink) for i in self.linkages]

    @property
    def sources(self):
        """Source Locations of the System"""
        return sorted({i[0] for i in self.pairs})

    @property
    def sinks(self):
        """Sink Locations of the System"""
        return sorted({i[1] for i in self.pairs})
