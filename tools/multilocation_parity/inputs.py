"""Original chronological inputs and installed technology data from ml-sp-milp."""

from pathlib import Path

import numpy as np
import pandas as pd

HOURS = 8760
GAS_YEAR = 2020
DATA = Path(__file__).parent / "data"
SITES = ("HO", "SD", "NY")
SOURCES = SITES[:2]
LIMIT = 1_000_000
STORE = 10_000
DISTANCE = {"HO": 2366, "SD": 2620}
# activity basis, capex + fixed opex, variable opex, resource conversion
PLANTS = {
    "PV": (1333262 + 22623, 0, {"Solar": -1, "Power": 1}),
    "WF": (1462000 + 43000, 4953, {"Wind": -1, "Power": 1}),
    "SMRH": (
        2520000 + 945000,
        51.5,
        {
            "Power": -1.11,
            "CH4": -3.76,
            "H2O": -23.7,
            "H2": 1,
            "CO2_Vent": 1.03,
            "CO2": 9.332,
        },
    ),
    "AWE": (
        1100000 + 16918,
        0,
        {"Power": -1, "H2": 0.019, "O2": 0.7632, "H2O": -0.1753},
    ),
    "AQoff_SMR": (5.52, 4.14, {"Power": -1.28, "CO2_AQoff": 1, "CO2": -1}),
    "H2FC": (1600000, 3.5, {"H2": -0.05, "Power": 1}),
    "LiI": (3516428 + 87910, 0, {"Power": -1, "battery": 1}),
    "LiI_discharge": (0, 0, {"Power": 1, "battery": -1}),
}
INSTALLED = {
    site: (("PV", "WF", "SMRH", "AWE", "AQoff_SMR") if site in SOURCES else ("H2FC",))
    + ("LiI", "LiI_discharge")
    for site in SITES
}


def load_inputs():
    """Normalize over the full source year BEFORE slicing a validation window."""
    data = {}
    for site, filename in [("HO", "ho_solar19.csv"), ("SD", "sd_solar19.csv")]:
        weather = pd.read_csv(DATA / filename)
        for plant, column in [("PV", "dni"), ("WF", "wind_speed")]:
            data[f"{site}_{plant}"] = (
                weather[column] / weather[column].max()
            ).to_numpy()
    load = pd.read_csv(DATA / "NYC_load.csv")["Load"]
    data["demand"] = (80 * load / load.max()).to_numpy()
    prices = pd.read_csv(
        DATA / "Henry_Hub_Natural_Gas_Spot_Price_Daily.csv",
        skiprows=5,
        names=["date", "CH4"],
    )
    dates = pd.to_datetime(prices["date"], format="%m/%d/%Y")
    prices = prices[dates.dt.year == GAS_YEAR].copy()
    prices.index = dates[dates.dt.year == GAS_YEAR].dt.strftime("%j").astype(int)
    prices = (
        prices["CH4"].dropna().sort_index().reindex(range(1, 366)).ffill().bfill()
        / 22.4
    )
    # The source uses sample standard deviation and sequential neighbour averaging.
    lower, upper = prices.mean() - 3 * prices.std(), prices.mean() + 3 * prices.std()
    for i in range(len(prices)):
        if prices.iloc[i] < lower or prices.iloc[i] > upper:
            prices.iloc[i] = (prices.iloc[i - 1] + prices.iloc[i + 1]) / 2
    data["gas"] = np.repeat((prices / prices.max()).to_numpy(), 24)
    if any(len(value) != HOURS for value in data.values()):
        message = "Expected 8,760 hourly values for every input"
        raise ValueError(message)
    return data
