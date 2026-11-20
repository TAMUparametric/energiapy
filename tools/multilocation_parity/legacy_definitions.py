"""
Installed definitions copied from Rahul Kakodkar's ml-sp-milp.ipynb.

Kuru db35908bd9056ef8f484c425bf2d2cb428677a83; original notebook blob
 e40d5c1ae7bcdb74d20de905134e6bc3f51da122. Only unused definitions are omitted.
"""

from energiapy.components.process import Process, VaryingProcess
from energiapy.components.resource import Resource, VaryingResource


def resource_definitions():
    """Construct the archived resource definitions without altering parameters."""
    limit = 10**6
    Solar = Resource(name="Solar", cons_max=limit, basis="MW", label="Solar Power")
    Wind = Resource(name="Wind", cons_max=limit, basis="MW", label="Wind Power")
    Power = Resource(
        name="Power",
        basis="MW",
        label="Power generated",
        varying=[VaryingResource.DETERMINISTIC_DEMAND],
        demand=True,
    )
    H2 = Resource(name="H2", basis="tons", label="Hydrogen")
    CO2_AQoff = Resource(
        name="CO2_AQoff",
        basis="tons",
        label="Carbon dioxide - sequestered",
        store_max=10000,
    )
    H2O = Resource(
        name="H2O",
        cons_max=limit,
        price=0.001,
        basis="tons",
        label="Water",
        block="Resource",
    )
    CH4 = Resource(
        name="CH4",
        cons_max=limit,
        price=1,
        basis="tons",
        label="Natural gas",
        varying=[VaryingResource.DETERMINISTIC_PRICE],
    )
    CO2 = Resource(name="CO2", basis="tons", label="Carbon dioxide", block="Resource")
    CO2_Vent = Resource(
        name="CO2_Vent",
        sell=True,
        basis="tons",
        label="Carbon dioxide - Vented",
    )
    O2 = Resource(name="O2", sell=True, basis="tons", label="Oxygen")
    return {
        "Solar": Solar,
        "Wind": Wind,
        "Power": Power,
        "H2": H2,
        "CO2_AQoff": CO2_AQoff,
        "H2O": H2O,
        "CH4": CH4,
        "CO2": CO2,
        "CO2_Vent": CO2_Vent,
        "O2": O2,
    }


def definitions():
    """Construct the archived resources and installed processes, unchanged."""
    resources = resource_definitions()
    limit = 10**6
    LiI = Process(
        name="LiI",
        storage=resources["Power"],
        capex=3516428,
        fopex=87910,
        vopex=0,
        store_max=10000,
        prod_max=limit,
        label="Lithium-ion battery",
        basis="MW",
    )
    WF = Process(
        name="WF",
        conversion={resources["Wind"]: -1, resources["Power"]: 1},
        capex=1462000,
        fopex=43000,
        vopex=4953,
        prod_max=limit,
        label="Wind mill array",
        varying=[VaryingProcess.DETERMINISTIC_CAPACITY],
        basis="MW",
    )
    PV = Process(
        name="PV",
        conversion={resources["Solar"]: -1, resources["Power"]: 1},
        capex=1333262,
        fopex=22623,
        vopex=0,
        prod_max=limit,
        varying=[VaryingProcess.DETERMINISTIC_CAPACITY],
        label="Solar PV",
        basis="MW",
    )
    SMRH = Process(
        name="SMRH",
        conversion={
            resources["Power"]: -1.11,
            resources["CH4"]: -3.76,
            resources["H2O"]: -23.7,
            resources["H2"]: 1,
            resources["CO2_Vent"]: 1.03,
            resources["CO2"]: 9.332,
        },
        capex=2520000,
        fopex=945000,
        vopex=51.5,
        prod_max=limit,
        label="Steam methane reforming + CCUS",
    )
    H2FC = Process(
        name="H2FC",
        conversion={resources["H2"]: -0.05, resources["Power"]: 1},
        capex=1.6 * 10**6,
        vopex=3.5,
        fopex=0,
        prod_max=limit,
        label="hydrogen fuel cell",
    )
    AWE = Process(
        name="AWE",
        conversion={
            resources["Power"]: -1,
            resources["H2"]: 0.019,
            resources["O2"]: 0.7632,
            resources["H2O"]: -0.1753,
        },
        capex=1.1 * 10**6,
        fopex=16918,
        vopex=0,
        prod_max=limit,
        label="Alkaline water electrolysis (AWE)",
        citation="Demirhan et al. 2018 AIChE paper",
    )
    AQoff_SMR = Process(
        name="AQoff_SMR",
        conversion={
            resources["Power"]: -1.28,
            resources["CO2_AQoff"]: 1,
            resources["CO2"]: -1,
        },
        capex=5.52,
        vopex=4.14,
        fopex=0,
        prod_max=limit,
        label="Offshore aquifer CO2 sequestration (SMR)",
    )
    return {
        **resources,
        "LiI": LiI,
        "WF": WF,
        "PV": PV,
        "SMRH": SMRH,
        "H2FC": H2FC,
        "AWE": AWE,
        "AQoff_SMR": AQoff_SMR,
    }
