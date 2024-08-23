"""Custom Warning Classes
"""


class OverWriteWarning(UserWarning):
    """Warning for overwriting attributes

    Attributes:
        cmp (str): Component being overwritten

    """

    def __init__(self, component):
        self.message = (
            f'\nA {component} was already defined.'
            '\nOverwriting. Set Scenario.ok_overwrite=False, to enforce strictly'
            '\nThis should not cause any modeling issues.'
            '\nCheck Scenario defaults if unintended.'
            '\nOnly one instance of Horizon, Network, Cash, and Land are allowed'
        )

    def __str__(self):
        return self.message


class InconsistencyWarning(UserWarning):
    """Warning for spatiotemporal inconsistencies

    Attributes:
        component (str): Component with inconsistency
        attr (str): Attribute with inconsistency
        spt (str): Spatial Component
        tmp (str): Scale
        scale_upd (str): Updated Scale
    """

    def __init__(self, component, attr, spt, tmp, scale_upd):
        self.message = (
            f'\n{component}.{attr}:Inconsistent temporal scale for {spt} at {tmp}.'
            f'\nUpdating to {scale_upd}'
            f'\nSet Scneario.ok_inconsistent=False, to enforce strictly'
        )

    def __str__(self):
        return self.message
