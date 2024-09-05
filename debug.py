from src.energiapy.components import *
from src.energiapy.environ import *
from pandas import DataFrame
from dataclasses import fields, field, dataclass

s = Scenario(default=True)

# s.h2 = Horizon({'days': 2, 'hours': 12})
s.hor = Horizon(birth=[2, 12])
s.net = Network(['madgaon', 'ponje', 'cacoda'])  # , link_all=True)
s.alink = Linkage(source=s.madgaon, sink=s.ponje, bi=True, distance=50)
s.blink = Linkage(source=s.ponje, sink=s.cacoda, bi=False, distance=80)
s.clink = Linkage(source=s.cacoda, sink=s.madgaon, bi=True, distance=100)
s.dlink = Linkage(source=s.madgaon, sink=s.ponje, bi=False, distance=200)

a = DataFrame({'a': list(range(2))})
b = DataFrame({'b': list(range(24))})

s.csh = Cash(
    spend={
        s.madgaon: True,
        s.ponje: {s.t2: (2, a)},
        s.cacoda: a,
        s.network: {s.t2: [5, 7]},
    },
    # label='cash',
    basis='USD',
)

s.H2 = Resource(
    # sell={s.t0: [0, 4], s.t1: [a, 34], s.t2: (a, b)},
    sell_price={
        s.madgaon: {s.t1: (2, a)},
        s.ponje: {s.t1: (2, b)},
        s.cacoda: 300,
    },
)

s.Solar = Resource(buy=True, basis='MW', label='Solar Power')


s.Wind = Resource(buy=a, basis='MW', label='Wind Power')


s.Power = Resource(basis='MW', label='Power generated')


s.Uranium = Resource(
    buy=DataFrame({'a': [i for i in range(24)]}),
    buy_price=42.70 / (250 / 2),
    basis='kg',
    label='Uranium',
)


# s.H2_L = Resource(sell=(0, 23), basis='tons', label='Hydrogen')


# s.CO2_AQoff = Resource(basis='tons', label='Carbon dioxide - sequestered')


s.H2O = Resource(buy=(20, 50), buy_price=b, basis='tons', label='Water')


s.CH4 = Resource(buy=[20, 40], buy_price=20, basis='tons', label='Natural gas')


s.CO2 = Resource(basis='tons', label='Carbon dioxide', block='Resource')


s.CO2_Vent = Resource(
    basis='tons',
    label='Carbon dioxide - Vented',
    sell_price=(2, 20),
    sell_emission={s.gwp: b},
)


s.O2 = Resource(sell=[20, True], basis='tons', label='Oxygen')


s.CO2_DAC = Resource(basis='tons', label='Carbon dioxide - captured')
s.Power = Resource(buy=[0, a], basis='MW', label='Power generated')


s.LiR = Material(
    use_emission={s.gwp: {s.t2: 1.484}},
    use={s.ponje: 1.5},
    basis='kg',
    label='Lithium Reserves',
    citation='Nelson Bunyui Manjong (2021)',
)


s.WF = Process(
    conversion={s.Power: {X(0): {s.Wind: -1}, X(1): {s.Wind: -1}}},
    produce=[(0, 3), (3, 5)],
    capex={s.madgaon: {s.t1: {1462000, I(202233)}}},
    opex={4953, I(70)},
    capacity=1000,
    setup_emission={s.gwp: 50, s.odp: 2900},
    setup_use={s.LiR: 1.5, s.land: 30},
    locations=[s.madgaon, s.ponje],
    label='Wind mill array',
    basis='MW',
)


s.PV = Process(
    sell_price={s.Power: 30},
    credit={s.Power: DataFrame({'a': [2]})},
    conversion={s.Power: {X(1): {s.Solar: -1.2}, X(2): {s.Solar: -1.5}}},
    capex={X(0): 1333, X(1): 1444, X(2): 1555},
    opex=22623,
    capacity={X(0): 3000, X(1): 4000, X(2): 5000},
    locations=s.cacoda,
    label='Solar PV',
    basis='MW',
)


s.SMRH = Process(
    setup_use={s.land: 50},
    conversion={
        s.H2: {
            s.Power: -1.11,
            s.CH4: -3.76,
            s.H2O: -23.7,
            s.CO2_Vent: 1.03,
            s.CO2: 9.332,
        }
    },
    capex={
        2520000,
    },
    opex={51.5, I(945000)},
    capacity=[1000],
    label='Steam methane reforming + CCUS',
)

s.NGCC = Process(
    buy_price={s.CH4: 4, s.H2O: 20},
    conversion={
        s.Power: {
            s.CH4: -0.108,
            s.H2O: -10,
            s.CO2_Vent: 0.297 * 0.05,
            s.CO2: 0.297 * 0.95,
        }
    },
    capex=2158928,
    opex={4090, I(53320)},
    capacity=[1, 100],
    label='NGCC + 95% CC',
)
s.SMR = Process(
    capex=2400,
    opex={0.03, I(800)},
    conversion={s.H2: {s.Power: -1.11, s.CH4: -3.76, s.H2O: -23.7, s.CO2_Vent: 9.4979}},
    capacity=1000,
    label='Steam methane reforming',
)
s.H2FC = Process(
    buy_price={s.H2: 2},
    sell={s.Power: 20},
    conversion={s.Power: {s.H2: -0.050}},
    capex=1.6 * 10**6,
    opex=3.5,
    capacity=[1000, 2000],
    label='hydrogen fuel cell',
)
s.DAC = Process(
    capex=0.02536,
    opex=0.634,
    conversion={s.CO2_DAC: {s.Power: -0.193, s.H2O: -4.048}},
    capacity=1000,
    label='Direct air capture',
)
# s.PSH = Process(conversion = {s.Power: 0.6}, capex = 3924781, fopex= 17820, vopex = 512.5, store = 10000, capacity=1000, label='Pumped storage hydropower', basis = 'MW')
s.ASMR = Process(
    buy={s.Uranium: 40},
    conversion={s.Power: {s.Uranium: -4.17 * 10 ** (-5), s.H2O: -3.364}},
    capex=7988951,
    opex=I(0.04 * 0.730),
    capacity=1000,
    label='Small modular reactors (SMRs)',
    locations=s.madgaon,
)
s.AWE = Process(
    setup_use={s.land: (0, 20)},
    conversion={s.H2: {s.Power: -1, s.O2: 0.7632, s.H2O: -0.1753}},
    capex={1.1 * 10**6, I(20)},
    opex=I(16918),
    capacity=True,
    label='Alkaline water electrolysis (AWE)',
    citation='Demirhan et al. 2018 AIChE paper',
)

s.LiI = Storage(capacity=[2000], inventory=s.Power, capacity_in=[40], capacity_out=[20])
s.LiI2 = Storage(capacity=[2000], inventory={s.Power: 0.6})
s.H2Stg = Storage(
    capacity=[2000], inventory={s.H2: {X(0): {s.Power: 0.8}, X(1): {s.Power: 0.9}}}
)
